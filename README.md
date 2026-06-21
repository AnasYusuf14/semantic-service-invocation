LLM Destekli Semantik Servis Çağırma
Örnek veri seti
Burada en iyi yol, OpenAPI tanımlı servislerden ve sizin üreteceğiniz doğal dil isteklerinden bir görev veri seti oluşturmaktır. OpenAPI’nin makinece okunabilir API tanımı sağlaması bu amaç için çok uygundur.
Veri seti önerisi
5 API alanı:
●	hava durumu
●	uçuş/otel
●	ürün arama
●	sipariş yönetimi
●	takvim/randevu
Her API için:
●	5–10 operasyon
●	her operasyon için 10–20 doğal dil ifade
Toplam:
●	250–400 doğal dil sorgu
●	beklenen çıktı:
○	doğru servis
○	doğru endpoint
○	doğru parametreler
○	opsiyonel semantik kavram etiketi
İsterseniz operasyonları ontoloji kavramlarına bağlayın:
●	BookFlight
●	SearchHotel
●	CreateOrder
●	GetForecast
Deney tasarımı
Karşılaştırma:
1.	Rule-based intent mapping
2.	Embedding tabanlı benzerlik
3.	LLM doğrudan servis seçimi
4.	LLM + ontoloji doğrulama
○	en güçlü yöntem adayınız bu olabilir
Ölçütler
●	Intent accuracy
●	Endpoint selection accuracy
●	Parameter filling accuracy
●	End-to-end task success
●	Hallucination rate
Hata kategorileri
●	yanlış servis
●	doğru servis / yanlış endpoint
●	eksik parametre
●	ontolojiyle uyumsuz çağrı
●	hayali alan/parametre
Makale için tablo/şekil
●	Yöntem bazlı accuracy tablosu
●	Hata türleri pasta grafiği
●	Domain bazında başarı karşılaştırması
Haftalık Plan
Hafta 1
●	LLM + API entegrasyonu
●	OpenAPI inceleme
Hafta 2
●	Veri seti oluşturma (NL → API çağrısı)
Hafta 3
●	Rule-based baseline
Hafta 4
●	Embedding tabanlı eşleşme
Hafta 5
●	LLM ile doğrudan servis çağırma
Hafta 6
●	Ontoloji ile doğrulama katmanı
Hafta 7
●	Accuracy ve hata analizi
Hafta 8
●	Makale yazımı


