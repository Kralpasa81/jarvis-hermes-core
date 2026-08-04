# Simple CSV-JSON Transformer Tool
# Kralpasa81/Mustafa - 2024-08-04 daily contribution

class DataTransformer:
    """
    Basit bir CSV ve JSON formatları arasında dönüştürme aracı.
    Gerçek veriler kullanılmamakta, sadece mock(cas) test amaçlı örnekler.
    """
    
    def csv_to_json(self, csv_content: str) -> str:
        """
        CSV formatındaki veriyi JSON formatına dönüştürür.
        Örneğin,test amaçlı mock data ile çalışır.
        """
        import csv
        import json
        
        # CSV'yi parse et
        lines = csv_content.splitlines()
        reader = csv.DictReader(lines)
        data = [row for row in reader]  
        
        # JSON'a dönüştür
        return json.dumps(data, indent=2)
    
    def json_to_csv(self, json_content: str) -> str:
        """
        JSON formatındaki veriyi CSV formatına dönüştürür.
        """
        import json
        import csv
        from io import StringIO
    
        data = json.loads(json_content)
        
        if not data:
            return ""  # Boş veri durumunda boş döndür
    
        # CSV oluştur
        output = StringIO()
        fieldnames = data[0].keys() if data else []
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()

    def mock_csv_data(self):
        """
        Test amaçlı mock csv verisi oluşturur.
        """
        return '''\nAd,Soyad,Yaş,Meslek\n
Ali,Yılmaz,30,Yazılım Mühendisi\nAyşe, Kaya,28, Veri Bilimci\nMehmet, Öztürk,35, Sistem Yöneticisi\nFatma, Gül,32, UX Tasarımcısı\nAhmet, Uslu,29, DevOps Mühendisi'''