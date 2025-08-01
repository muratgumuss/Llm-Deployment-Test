
import requests
import json
import gradio as gr
#1. Gerekli Kütüphanelerin İçe Aktarılması

"""
typing.final ve matplotlib.pyplot.hist aslında bu kodda kullanılmıyor, kaldırılabilir.
requests: HTTP istekleri yapmak için kullanılır.
json: JSON verilerini işlemek için kullanılır.
gradio: Web tabanlı arayüz oluşturmak için kullanılır
"""
url = "http://localhost:11434/api/generate"

headers = {
    "Content-Type": "application/json",
}
#2. API URL ve Header Tanımlamaları
"""
API'ye istek yapılacak adres ve içerik tipini belirten başlıklar tanımlanıyor.
"""
#3. Geçmiş (history) Listesi
"""
Kullanıcının yazdığı tüm promptlar burada saklanıyor. Böylece önceki girdiler de modele gönderilebiliyor.
"""
history = []

#4. Ana Fonksiyon: generate_response
"""
Kullanıcıdan gelen prompt, history listesine ekleniyor.
Tüm geçmiş promptlar birleştirilip (final_prompt) modele gönderiliyor.
API'ye POST isteği gönderiliyor.
Eğer istek başarılıysa (status_code == 200), dönen JSON içinden modelin cevabı alınıp kullanıcıya dönülüyor.
Hata olursa hata mesajı dönülüyor.
"""
def generate_response(prompt):
    history.append(prompt)
    final_prompt = "\n".join(history)

    data = {
        "model": "codeguru",
        "prompt": final_prompt,
        "stream": False,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response = response.text
        data = json.loads(response)
        actual_response = data['response']
        return actual_response
    else:
        return {"error": response.text}
 #5. Gradio Arayüzü Oluşturulması
"""
Gradio ile bir web arayüzü oluşturuluyor.
Kullanıcıdan metin girişi alınıyor ve cevap olarak metin gösteriliyor.
Arayüz başlığı ve açıklaması belirleniyor.
"""   
interface = gr.Interface(
    fn=generate_response,
    inputs=gr.Textbox(lines=4, placeholder="Enter your prompt here"),
    outputs="text",
    title="Code Assistant",
    description="A simple code assistant that generates code based on your prompt.",
)
#6. Arayüzün Başlatılması
"""
Gradio arayüzü başlatılıyor ve kullanıcıya sunuluyor.
"""
interface.launch()

"""
Kullanıcı arayüze prompt girer.
Prompt geçmişe eklenir ve API'ye gönderilir.
API'den gelen cevap kullanıcıya gösterilir.
"""

"""
Oluşturulan modelfile, kendi yerel LLM (Large Language Model) sunucunuzu (örneğin Ollama gibi) başlatmak ve yapılandırmak için kullanılır. Bu dosya, modelin hangi temel modelden türetileceğini, varsa ek ayarları ve metadata’yı belirtir. Yani, modelfile bir tür “model tarif dosyasıdır”.

Senin örneğinde:

codeguru: Bu, modelfile ile tanımladığın ve Ollama gibi bir sunucuya yüklediğin modelin adı. API’ye istek gönderirken "model": "codeguru" diyerek bu modeli kullanmasını söylüyorsun.
llama ile çalıştırmak: Eğer modelfile içinde FROM llama2 gibi bir satır varsa, codeguru aslında Llama2 tabanlı bir model oluyor. Yani codeguru senin verdiğin isim, arka planda Llama2 çalışıyor.
Özetle:

modelfile, modelin nasıl oluşturulacağını ve hangi temel modeli kullanacağını tanımlar.
codeguru, bu modelfile’dan oluşturulan ve API’de kullanılacak modelin adıdır.
Llama ile çalıştırmak, codeguru’nun temelinde Llama2 gibi bir model olduğu anlamına gelir.
"""

"""
Buradaki API adresi (http://localhost:11434/api/generate) senin kendi bilgisayarında (localhost) çalışan bir LLM (büyük dil modeli) sunucusuna aittir. Bu adresi şu şekilde biliyoruz:

Senin kurduğun LLM sunucusu (örneğin Ollama, LM Studio, Open Interpreter, v.s.) genellikle bir port üzerinden HTTP API sunar.
Ollama gibi araçlarda, model yüklediğinde ve çalıştırdığında, genellikle varsayılan olarak localhost:11434 portunda bir API açılır.
API dökümantasyonunda veya başlatma komutlarında hangi portun ve endpoint’in kullanılacağı belirtilir.
Kodda "model": "codeguru" olarak belirttiğin model, Ollama veya benzeri sunucuda yüklü olan modelin adıdır.
Kısacası:
Bu adresi, kullandığın LLM sunucusunun dökümantasyonundan veya başlatma komutundan öğreniyoruz. Eğer farklı bir port veya endpoint kullanıyorsan, kodda da onu belirtmelisin.
"""

"""
#streamlit ile basit bir kod asistanı uygulaması
import requests
import json
import streamlit as st

url = "http://localhost:11434/api/generate"
headers = {"Content-Type": "application/json"}
history = []

st.title("Code Assistant")
st.write("A simple code assistant that generates code based on your prompt.")

prompt = st.text_area("Enter your prompt here", height=100)

if st.button("Send"):
    if prompt.strip():
        history.append(prompt)
        final_prompt = "\n".join(history)
        data = {
            "model": "codeguru",
            "prompt": final_prompt,
            "stream": False,
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            data = response.json()
            st.success(data['response'])
        else:
            st.error(response.text)
"""

"""
Arayüzde sorunun cevabının yavaş dönmesi birkaç farklı nedene bağlı olabilir:

Bilgisayarının Donanımı:
Eğer yerel olarak çalışan LLM (ör. Ollama, LM Studio) kullanıyorsan, modelin yanıt süresi bilgisayarının işlemci (CPU), bellek (RAM) ve varsa ekran kartı (GPU) gücüne doğrudan bağlıdır. Özellikle büyük modellerde yavaşlık normaldir.

Modelin Büyüklüğü ve Karmaşıklığı:
Daha büyük ve karmaşık modeller (ör. Llama2-13B gibi) daha fazla kaynak tüketir ve yanıtı daha geç üretir.

Arka Planda Çalışan Diğer İşlemler:
Bilgisayarında başka ağır uygulamalar açıksa, modelin yanıt süresi uzayabilir.

API ve Kodun Çalışma Şekli:
Kodun, modeli her seferinde sıfırdan yüklemiyorsa ve model bellekte hazırsa, yanıt daha hızlı gelir. Ancak model her istekten önce yükleniyorsa ciddi yavaşlık olur.

Stream (Akış) Özelliği:
Kodda "stream": False olarak ayarlanmış. Eğer model ve API akışlı yanıtı destekliyorsa, "stream": True ile yanıtı parça parça daha hızlı görebilirsin.

Özet:
Yavaşlık çoğunlukla bilgisayarının donanımı ve kullandığın modelin büyüklüğü ile ilgilidir. Daha hızlı yanıt için daha küçük bir model seçebilir veya güçlü bir donanım kullanabilirsin.
"""