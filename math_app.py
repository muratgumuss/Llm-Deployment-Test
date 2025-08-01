# 1. GEREKLİ KÜTÜPHANELERİN İMPORTU
"""
streamlit: Web tabanlı interaktif uygulamalar (özellikle veri bilimi ve AI için) oluşturmanı sağlar.
as st: Kütüphaneye kısa ad verilir, örn. st.write(), st.button() gibi kullanmak için.
ChatGroq: Groq LLM API’sini LangChain üzerinden bağlamak için kullanılan sınıf.
Gemma2-9b-It gibi modelleri çalıştırmak için kullanılır.
LLMMathChain: Sayısal ifadeleri çözümleyip LLM üzerinden matematik işlemi yaptırmak için bir zincir (chain).
LLMChain: Genelleştirilmiş prompt-template ile LLM yanıtı dönen yapı.
PromptTemplate: Dinamik olarak LLM'e gönderilecek prompt’ları formatlamaya yarar.
Wikipedia verilerine erişim sağlar (topluluk destekli wrapper).
Tool: LangChain’de LLM’e bağlanan işlevsel yardımcı araç tanımıdır.
initialize_agent: Birden fazla Tool’u bağlayarak görevleri üstlenebilen "agent" nesnesi üretir.
AgentType.ZERO_SHOT_REACT_DESCRIPTION: Tool açıklamalarına göre uygun aracı prompt analizine dayalı seçen zero-shot agent türüdür.
"""
import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMMathChain, LLMChain  # Fixed typo: LLMMAthChain -> LLMMathChain
from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, initialize_agent
from langchain.callbacks import StreamlitCallbackHandler

#2. SAYFA BAŞLIĞI VE GÖRÜNÜM
# Uygulama başlığını ve tarayıcı sekmesinde görünecek başlığı ayarlar.
st.set_page_config(page_title="Text to Math Solver and Data Search Assistant")
st.title("Text to Math Problem Solver Using Gemma 2")
#3. GROQ API KEY GİRİŞİ
"""
Yan panelden API anahtarı girişi alınır.

st.stop(): API key girilmemişse uygulamayı durdurur.
"""
groq_api_key = st.sidebar.text_input(label="Groq API Key", type="password")

if not groq_api_key:
    st.info("Please add your Groq Api Key to continue")
    st.stop()

#4. LLM TANIMLAMA
"""
Groq LLM’den Gemma2-9b-It modelini seçer.

Artık bu LLM, soruları yanıtlamaya hazırdır.
"""
llm = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

#5. WIKIPEDIA TOOL
"""
Wikipedia API wrapper’ı çalıştırılır.

Tool: Wikipedia’dan bilgi çekme aracı haline getirilir.
"""
# Initialize the tools
wikipedia_wrapper = WikipediaAPIWrapper()
wikipedia_tool = Tool(
    name="Wikipedia",
    func=wikipedia_wrapper.run,
    description="A tool searching the internet to find various information"
)
"""
func=wikipedia_wrapper.run ifadesi Python’a özgü ama aslında C#’taki “delegate” ya da “lambda expression” kullanımıyla benzer bir mantığa sahiptir.

Bunu tüm detaylarıyla aşağıda açıklıyorum:
Python'da fonksiyonlar birer first-class object’tir.

Yani:

    Bir fonksiyonu bir değişkene atayabiliriz.

    Bir fonksiyonu parametre olarak başka bir fonksiyona verebiliriz.

    Bir fonksiyonun adını .run gibi belirterek başka yapılara doğrudan verebiliriz.

compiler o satıra geldiğinde fonksiyonun referansını bildiği için kendi çalıştırıyor yani
ChatGPT:

Evet, tam olarak öyle! 👇
Derleyici veya yorumlayıcı (Python'da interpreter) o satıra geldiğinde fonksiyonun referansını bildiği için fonksiyonu sen çağırmadığın sürece çalıştırmaz — ama doğru zamanda, doğru yerden o fonksiyonu çağıracak şekilde hazırda tutar.

LangChain Agent Bu Mekanizmayı Nasıl Kullanır?

Agent şu adımları takip eder:

    Kullanıcı bir soru yazar: "Atatürk kimdir?"

    Agent bakar: Bu soruya en uygun Tool hangisi? (Tool açıklamalarına göre karar verir — description alanı burada önemli)

    Doğru Tool'u bulur. Örneğin Wikipedia.

    Şunu yapar: tool.func("Atatürk kimdir?")

    Bu da wikipedia_wrapper.run("Atatürk kimdir?") anlamına gelir.

Agent bu func’u çağıracağı için bizim sadece referansı vermemiz yeterlidir.

"""
#6. MATEMATİK HESAPLAYICI VE HATA YÖNETİMİ
"""
LLM destekli matematiksel ifade çözücü zincir oluşturulur.

Matematik işlemlerini try/except bloğu ile sararak "division by zero" gibi hataları yakalar.

Tool haline getirilir:
"""

# Initialize the Math Tool with error handling
math_chain = LLMMathChain.from_llm(llm=llm)

def safe_calculator(expression):
    """Calculator with error handling for mathematical operations"""
    try:
        result = math_chain.run(expression)
        return result
    except ValueError as e:
        if "division by zero" in str(e).lower():
            return "Error: Division by zero is undefined in mathematics. Please try a different expression."
        else:
            return f"Mathematical error: {str(e)}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

calculator = Tool(
    name="Calculator",
    func=safe_calculator,
    description="A tool answering math related questions. Only input mathematical expressions. Handles division by zero gracefully."
)

#7. MANTIKSAL SORU YANITLAMA – PROMPT VE ZİNCİR
"""
Agent’e gönderilecek açıklayıcı prompt. Cevabı adım adım ve açıklamalı ister.

"""
prompt = """
You are agent tasked for solving mathematical questions. Logically arrive at the solution and provide a detailed explanation
and display it point wise for the question below
Question:{question}
Answer:
"""

prompt_template = PromptTemplate(
    input_variables=["question"],
    template=prompt
)

#8. AGENT OLUŞTURMA
"""
Üç farklı Tool bağlanarak agent oluşturulur.

ZERO_SHOT_REACT_DESCRIPTION: Agent, verilen açıklamaya göre doğru Tool’u kendisi seçer.
"""

# Combine all the tools into chain
chain = LLMChain(llm=llm, prompt=prompt_template)  # Fixed typo: LLmChain -> LLMChain
reasoning_tool = Tool(
    name="Reasoning Tool",
    func=chain.run,
    description="A tool for answering logic-based and reasoning questions."
)

# Initialize the agents
assistant_agent = initialize_agent(
    tools=[wikipedia_tool, calculator, reasoning_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    handle_parsing_errors=True
)

#9. CHAT MESAJLARINI SAKLAMA ve GÖRÜNTÜLEME
"""
Uygulamanın geçmiş sohbeti session_state’te saklanır.
Kullanıcı ve asistan mesajları Streamlit chat formatında ekrana basılır.
"""
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "I am a math chatbot who can answer all your math questions"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

#10. KULLANICIDAN SORU ALMA ve CEVAP ÜRETME
"""
İşleyiş:

    Kullanıcı soruyu girer.

    Soruyu mesaj geçmişine ekler.

    StreamlitCallbackHandler oluşturulur (ajanın reasoning adımları canlı görünür).

    assistant_agent.run(question, callbacks=[st_cb]) → Agent soruyu işler ve doğru Tool’la çalışır.

    Yanıt gösterilir, session_state.messages’e eklenir.
"""
question = st.text_area("Enter your question:", "")

if st.button("Find my answer"):
    if question:
        with st.spinner("Generate Response"):
            try:
                # Add user message to session state
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Display user message
                with st.chat_message("user"):
                    st.write(question)
                
                # Create callback handler
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                
                # Get response from agent
                response = assistant_agent.run(question, callbacks=[st_cb])  # Fixed: pass question directly
                
                # Add assistant response to session state
                st.session_state.messages.append({'role': 'assistant', 'content': response})  # Fixed typo: assisttant -> assistant
                
                # Display response
                with st.chat_message("assistant"):
                    st.write(response)
              #11. HATA YAKALAMA
              # Herhangi bir hatada kullanıcıya genel hata mesajı verilir ve sohbet akışı bozulmadan devam eder.      
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                # Still add the user message to maintain chat flow
                if {"role": "user", "content": question} not in st.session_state.messages:
                    st.session_state.messages.append({"role": "user", "content": question})
                
                error_response = "I encountered an error while processing your question. Please try rephrasing or asking a different question."
                st.session_state.messages.append({'role': 'assistant', 'content': error_response})
                
                with st.chat_message("assistant"):
                    st.write(error_response)
    else:
        #12. GİRİŞ KONTROLÜ
        #Kullanıcı metin girmeden butona basarsa uyarı gösterilir.

        st.warning("Please enter the question")

"""
👤 Chat UI ile doğal dilde etkileşim sağlar.

🤖 Groq LLM (Gemma 2) ile bağlantı kurar.

➕ Sayısal ifadeleri çözer, hata yönetir.

🧠 Mantıksal açıklamalarla çözümler sunar.

🌐 Wikipedia'dan bilgi çeker.

🧩 LangChain agent ile doğru Tool’u seçer.
"""
"""
Soru 1: Agent en uygun Tool’a nasıl karar veriyor?

LangChain'de initialize_agent ile oluşturulan agent, soruyu analiz ederek hangi Tool’un uygun olduğunu "zero-shot" prompt reasoning yöntemiyle belirler.
Bu nasıl olur?

Agent şunu yapar:

    Her Tool’un description alanı vardır:

    Tool(
        name="Calculator",
        func=safe_calculator,
        description="A tool answering math related questions..."
    )
    Tool(
        name="Wikipedia",
        func=wikipedia_wrapper.run,
        description="A tool searching the internet to find various information"
    )

    Kullanıcı bir şey yazdığında, örneğin "Atatürk kimdir?", agent bu soruyu bir prompt içinde LLM’e verir:

        “Given the following tools and their descriptions, and the user input, decide which tool(s) to use in order to respond.”

    LLM bu açıklamalara bakarak karar verir:

        "Atatürk kimdir?" → Wikipedia tool mantıklı.

        "2+2 kaç eder?" → Calculator tool mantıklı.

    📌 Özet: Agent, Tool’ların açıklamasını LLM’e verir, LLM ise hangi Tool’u kullanacağını tahmin eder.

    İşte bu yüzden description alanlarını dikkatli yazmak kritik önemdedir.

🔀 Soru 2: Aynı cümlede hem bilgi hem matematiksel soru varsa ne olur?

Harika bir edge-case örneği!
Soru:

    "Atatürk kaç yaşında öldü ve ölüm yılı ile doğum yılı arasındaki fark nedir?"

Bu soruda:

    Wikipedia Tool → “Atatürk’ün doğum ve ölüm yılı” gibi bilgi çeker.

    Calculator Tool → 1938 - 1881 gibi bir işlemi yapar.

Peki LangChain Agent ne yapar?

Varsa:

    AgentType.ZERO_SHOT_REACT_DESCRIPTION → Tek aşamalı reasoning.

    AgentType.REACT_DOCSTORE gibi türler → Multi-step reasoning yapar (ara sonuçları kullanabilir).

Ama default ZERO_SHOT_REACT_DESCRIPTION genelde sadece bir Tool seçer.
Çözüm?

Eğer:

    Hem bilgi çekmek,

    Hem hesap yapmak istiyorsan…

Ya:

    Daha güçlü bir agent türü (multi-step support’lu) kullanmalısın (örnek: AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION)

Ya da:

    Kendi chain’ini yazmalısın:

        Wikipedia’dan bilgi çek

        Regex ile sayı çıkar

        Sonra Calculator’a ver

🧪 Örnek: Agent'ın reasoning yapması

LangChain, LLM'e bu tarz bir prompt verir (arkada görünmez):

You have access to the following tools:
Calculator: A tool answering math-related questions
Wikipedia: A tool searching the internet to find various information

Question: Atatürk kaç yaşında öldü?

LLM şöyle bir reasoning yapabilir:

    "I need to know his birth and death years, then subtract. I will use Wikipedia to get that info."

Ama bazı Agent tiplerinde bu adımları tek tek planlayıp Tool'lara dağıtmak gerekir.
🔧 Ne yapabilirim?

Senin gibi ileri düzey uygulama geliştiren biri için şu seçenekler var:

    Multi-step Agent kullan:

        AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION

    Custom Chain veya Router Chain yaz:

        Sorunun yapısına göre Wikipedia mı, Calculator mı karar ver.

        Ya da bir prompt ile önce veriyi çıkar, sonra hesap yap.

    Manual pipeline kur:

        LLM önce veriyi çeker,

        Sonra sen kodla onu sayıya çevirip işlem yaparsın.

İstersen bu örneği birlikte genişletip:

    Hem bilgi çeken,

    Hem işlem yapan
    bir multi-step agent veya custom chain yazabiliriz.

İlgini çekerse hemen başlayabiliriz.
"""