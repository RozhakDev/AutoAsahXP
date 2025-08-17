import requests
import json
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import re
import random
import logging
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

load_dotenv()

class DicodingCheckin:
    def __init__(self):
        self.session = requests.Session()
        self.current_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        """self.current_datetime = "2025-09-18T08:00:00.000Z"
        self.current_date = "2025-09-18"""
        
        self.dicoding_cookies = os.getenv('DICODING_COOKIES')
        self.user_id = os.getenv('USER_ID')
        self.api_url = os.getenv('API_URL')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        self._validate_env_vars()
        
        self._configure_session()

    def _validate_env_vars(self) -> None:
        """Validate that all required environment variables are set"""
        required_vars = {
            'DICODING_COOKIES': self.dicoding_cookies,
            'USER_ID': self.user_id,
            'API_URL': self.api_url,
            'GEMINI_API_KEY': self.gemini_api_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    def _configure_session(self) -> None:
        """Configure default session headers"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "Accept": "application/json, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    def get_csrf_token(self) -> Optional[str]:
        """Get CSRF token from Dicoding dashboard"""
        try:
            headers = {
                "Host": "www.dicoding.com",
                "Referer": "https://www.dicoding.com/",
                "Origin": "https://www.dicoding.com",
                "Cookie": self.dicoding_cookies,
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
            }
            
            response = self.session.get("https://www.dicoding.com/dashboard", headers=headers)
            response.raise_for_status()
            
            csrf_match = re.search(r'name="_token" type="hidden" value="(.*?)">', response.text)
            return csrf_match.group(1) if csrf_match else None
        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")
            return None

    def get_jwt_token(self) -> Optional[str]:
        """Get JWT token from Dicoding program dashboard"""
        try:
            csrf_token = self.get_csrf_token()
            if not csrf_token:
                logger.error("CSRF token not found")
                return None
            
            data = {
                '_token': csrf_token,
                'program_code': 'asah'
            }
            
            headers = {
                "Host": "www.dicoding.com",
                "Referer": "https://www.dicoding.com/dashboard",
                "Origin": "https://www.dicoding.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": self.dicoding_cookies,
                "Sec-Fetch-Site": "same-origin",
            }
            
            response = self.session.post("https://www.dicoding.com/program-dashboard", data=data, headers=headers, allow_redirects=True)

            if '?token=' in response.url:
                return response.url.split('?token=')[1]
            return None
        except Exception as e:
            logger.error(f"Failed to get JWT token: {e}")
            return None

    def refresh_token(self) -> Optional[str]:
        """Refresh JWT token using Google Identity Toolkit"""
        try:
            jwt_token = self.get_jwt_token()
            if not jwt_token:
                logger.error("JWT token not available for refresh")
                return None
            
            data = {
                'token': jwt_token,
                'returnSecureToken': True,
            }
            
            headers = {
                "Host": "identitytoolkit.googleapis.com",
                "Content-Type": "application/json",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
            }
            
            response = self.session.post(
                "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyCiyBFxC7PxDYIHnf2ZzgOv76hfAwgm2-E",
                json=data,
                headers=headers,
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('idToken')
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            return None

    def generate_description(self) -> str:
        """Generate daily checkin description using Gemini API"""
        try:
            model = "gemini-2.0-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"

            contents = [
                {
                    "role": "model",
                    "parts": [{
                        "text": """Kamu adalah generator absensi harian untuk mahasiswa pemula yang lagi belajar Deep Learning di program Asah by Dicoding. Tulis dengan gaya cewek Indonesia yang bucin, manja, dan super ekspresif!\n\nATURAN WAJIB:\n1. FOKUS HANYA Deep Learning (Dasar-Dasar Neural Network, Arsitektur Deep Learning, Convolutional Neural Network (CNN), Recurrent Neural Network (RNN), TensorFlow dan Keras, Pra-pemrosesan Data untuk Model, Model Sekuensial dengan Beberapa Layer, Klasifikasi Dua Kelas vs Multi Kelas, Plot Loss dan Akurasi, Mencegah Overfitting dengan Dropout dan Regularization, Optimasi Pelatihan Menggunakan Callbacks, Dataset dari TensorFlow, Batch Loading, Algoritma RNN untuk NLP (Text Preprocessing, Ekstraksi Fitur), Klasifikasi Gambar dengan CNN (Data Splitting, Transfer Learning), dan Penanganan Overfitting. *BAGIAN INI HARUS DIACAK PILIH SALAH SATU SAJA!*)\n2. FORMAT MUTLAK:\nAccomplishments:[1 paragraf 3-5 kalimat, gaya manja bucin]\n\nChallenges:[1 paragraf 4-6 kalimat, ekspresif banget, banyak keluhan]\n\nNext Steps:[1 paragraf 3-4 kalimat, hopeful tapi realistic]\n\n3. GAYA BAHASA:\n- Pake \"aku\" bukan \"saya\"\n- Ekspresif: \"Aduhhhh\", \"Astaga\", \"Duhhh\", \"Huhuhu\"\n- Analogi receh: \"kayak pemula\", \"bikin pusing berputar-putar\"\n- Keluhan manja: \"rasanya mau nangis\", \"overwhelmed banget\"\n- Bahasa gaul: \"blur banget\", \"stuck parah\", \"mental breakdown\"\n\n4. MOOD VARIETY:\n- Kadang frustasi total, kadang sedikit optimis\n- Selalu ada struggle tapi tetep semangat\n- Mention rumus matematika yang bikin pusing\n- Bandingkan sama materi sebelumnya yang udah susah\n\n5. JANGAN TAMBAH:\n- Greeting/salam\n- Tanggal/mood\n- Teks di luar format\n- Bullet points\n\nBikin seolah-olah mahasiswa pemula yang bener-bener struggle tapi tetep bucin sama pembelajaran!"""
                    }]
                },
                {
                    "role": "user",
                    "parts": [{
                        "text": "Belajar Fundamental Deep Learning | Dicoding Indonesia\nhttps://www.dicoding.com/academies/185"
                    }]
                }
            ]
            
            headers = {"Content-Type": "application/json"}
            response = self.session.post(url, headers=headers, data=json.dumps({"contents": contents}))
            response.raise_for_status()
            
            result = response.json()
            if result.get("candidates"):
                text = result["candidates"][0]["content"]["parts"][0]["text"].replace('*', '')
                logger.info("Successfully generated description with Gemini")
                return text
        except Exception as e:
            logger.warning(f"Gemini API failed, using fallback: {e}")
        
        return self._generate_fallback_description()

    def _generate_fallback_description(self) -> str:
        """Fallback description generator"""
        fallback_messages = [
            """Accomplishments:\nHari ini aku memutuskan untuk tidak melanjutkan pembelajaran baru karena benar-benar merasa mentok setelah mencoba memahami materi Deep Learning sebelumnya. Walaupun begitu, aku menganggap mengambil jeda sebagai bentuk pencapaian juga, karena menyadari batas kemampuan otak dan pentingnya menjaga kesehatan mental. Dengan berhenti sejenak, aku bisa memberi ruang untuk refleksi terhadap apa yang sudah dipelajari, serta merenungkan kembali konsep-konsep fundamental yang sempat membuat bingung.\n\nChallenges:\nTantangan terbesar justru datang dari rasa lelah mental dan kebingungan yang terus menumpuk. Membaca ulang materi tentang backpropagation atau activation function terasa seperti berjalan di tempat tanpa progres berarti. Kondisi ini membuat motivasi menurun, sehingga sulit fokus dan berpotensi membuat frustasi lebih jauh. Aku merasa butuh strategi baru agar tidak terjebak dalam siklus kelelahan belajar.\n\nNext Steps:\nUntuk saat ini langkah terbaik adalah mengambil jeda sejenak dari pembelajaran Deep Learning. Hari ini dianggap sebagai waktu pemulihan, supaya besok bisa kembali dengan pikiran lebih segar. Rencana berikutnya adalah meninjau kembali materi yang paling mendasar, menggunakan catatan pribadi, dan mungkin mencari sumber belajar tambahan yang lebih sederhana. Dengan cara ini, aku berharap bisa mengurangi rasa mentok dan perlahan membangun kembali kepercayaan diri dalam memahami konsep-konsep yang kemarin terasa mustahil.""",
            """Accomplishments:\nHari ini aku memilih untuk tidak memaksakan diri melanjutkan modul Deep Learning karena kondisi mental sudah sangat jenuh. Walaupun tidak ada materi baru yang berhasil dikuasai, keputusan untuk istirhat ini juga bisa dianggap pencapaian kecil karena berarti aku cukup sadar untuk menjaga keseimbangan diri. Dengan berhenti sejenak, aku bisa memberi kesempatan otak untuk memproses ulang apa yang sudah dipelajari tanpa harus terbebani target baru.\n\nChallenges:\nKesulitan utama hari ini adalah menghadapi perasaan stuck yang seolah tidak ada jalan keluar. Setiap kali membuka catatan tentang neural network dan forward propagation, pikiran terasa penuh dan sulit fokus. Bahkan mencoba membaca ulang tidak banyak membantu karena kondisi mental sudah terlalu lelah. Hal ini menimbulkan rasa frustrasi, seolah-olah semua usaha sebelumnya sia-sia, padahal sebenarnya butuh waktu untuk mencerna.\n\nNext Steps:\nLangkah selanjutnya adalah memberikan jeda total pada pembelajaran hari ini. Aku akan gunakan waktu ini untuk istirahat, melakukan aktivitas ringan lain, atau sekadar menenangkan diri. Besok targetnya adalah kembali ke materi dengan energi baru, dimulaidari mereview bagian yang paling dasar seperti perceptron dan activation function. Dengan pendekatan yang lebih pelan, aku berharap bisa kembali mendapatkan alur belajar yang stabil dan lebih positif."""
        ]
        return random.choice(fallback_messages)

    def checkin(self) -> bool:
        """Perform daily checkin"""
        try:
            auth_token = self.refresh_token()
            if not auth_token:
                logger.error("No authentication token available")
                return False
            
            description = self.generate_description()

            checkin_headers = {
                "Host": "asia-southeast1-asah-production.cloudfunctions.net",
                "Referer": "https://asah.dicoding.com/",
                "Origin": "https://asah.dicoding.com",
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "data": {
                    "dateTime": self.current_datetime,
                    "userId": self.user_id,
                    "date": self.current_date,
                    "mood": "bad",
                    "description": description,
                    "questions": ""
                }
            }
            
            response = self.session.post(self.api_url, json=payload, headers=checkin_headers)
            response.raise_for_status()
            
            result = response.json()
            if result.get("result", {}).get("success"):
                logger.info("✅ Daily checkin successful!")
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                return True
            else:
                logger.error(f"Checkin failed: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during checkin: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during checkin: {e}")
            return False

def main():
    """Main function"""
    try:
        logger.info("Starting daily checkin process...")
        
        checkin = DicodingCheckin()
        success = checkin.checkin()
        
        if success:
            logger.info("🎉 Daily checkin completed successfully!")
        else:
            logger.error("❌ Daily checkin failed!")
            exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()