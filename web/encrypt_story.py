from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import base64
import json
import os
import hashlib

def pad(data):
    """PKCS7 padding (byte-level)"""
    length = 16 - (len(data) % 16)
    return data + bytes([length] * length)

def validate_story(story_data):
    """Hikaye formatını doğrula"""
    required_fields = ["title", "steps"]
    step_types = ["choice", "quiz", "end"]
    
    # Ana alanları kontrol et
    for field in required_fields:
        if field not in story_data:
            raise ValueError(f"Eksik alan: {field}")
    
    # Adımları kontrol et
    for step_id, step in story_data["steps"].items():
        if "type" not in step or step["type"] not in step_types:
            raise ValueError(f"Geçersiz adım tipi: {step_id}")
        
        if step["type"] == "choice" and "options" not in step:
            raise ValueError(f"Seçim adımında options eksik: {step_id}")
        
        if step["type"] == "quiz" and "answers" not in step:
            raise ValueError(f"Quiz adımında answers eksik: {step_id}")

def encrypt_story(json_path, password, output_path=None):
    """
    JSON hikayeyi şifreler ve .enc dosyası oluşturur
    """
    try:
        # Çıkış dosyası adını belirle
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(json_path))[0]
            output_path = f"{base_name}.enc"
        
        # JSON oku ve doğrula
        with open(json_path, "r", encoding="utf-8") as f:
            story_data = json.load(f)
            validate_story(story_data)
        
        # JSON'u byte'a çevir
        story_str = json.dumps(story_data, ensure_ascii=False)
        story_bytes = story_str.encode("utf-8")
        
        # Padding uygula
        padded_data = pad(story_bytes)
        
        # Key ve IV
        key = hashlib.sha256(password.encode("utf-8")).digest()
        iv = get_random_bytes(16)
        
        # AES Şifreleme
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(padded_data)
        
        # IV + Ciphertext'i base64 encode et
        result = base64.b64encode(iv + ciphertext).decode("utf-8")
        
        # .enc dosyasına kaydet
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        print(f"✅ Şifrelenmiş hikaye '{output_path}' olarak kaydedildi")
        return output_path
        
    except FileNotFoundError:
        print(f"❌ Dosya bulunamadı: {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Geçersiz JSON formatı: {json_path}")
        return None
    except Exception as e:
        print(f"❌ Şifreleme hatası: {str(e)}")
        return None

def create_sample_stories():
    """
    Örnek hikaye dosyaları oluşturur
    """
    # Orman Macerası
    forest_story = {
        "title": "Orman Macerası",
        "description": "Büyülü ormanda kaybolmuş bir çocuğun macerası",
        "steps": {
            "start": {
                "id": "start",
                "text": "Merhaba {{name}}! Büyülü ormanda kaybolmuş durumdasın. Etrafında dev ağaçlar ve mistik sesler var. Ne yapacaksın?",
                "type": "choice",
                "background": "forest",
                "options": [
                    {"label": "🌲 Ormanda yürümeye devam et", "next": "forest_walk"},
                    {"label": "🏠 Uzaktaki kulübeye git", "next": "cabin"},
                    {"label": "🔍 Etrafı daha iyi araştır", "next": "investigate"}
                ]
            },
            "forest_walk": {
                "id": "forest_walk",
                "text": "{{name}}, ormanda yürürken büyülü bir yaratık ile karşılaştın! Sana bir matematik bulmacası sordu.",
                "type": "quiz",
                "question": "Büyücü: '5 elma + 3 elma kaç elma eder, {{name}}?'",
                "background": "forest",
                "answers": [
                    {"text": "7 elma", "correct": False},
                    {"text": "8 elma", "correct": True},
                    {"text": "9 elma", "correct": False}
                ]
            },
            "cabin": {
                "id": "cabin",
                "text": "{{name}}, kulübeye vardığında içeride yaşlı bir büyücü gördün! 'Merhaba cesur {{name}}! Sana bir soru soracağım.'",
                "type": "quiz",
                "question": "Büyücü: 'Hangi renk mavi + sarı karışımından çıkar?'",
                "background": "cabin",
                "answers": [
                    {"text": "Mor", "correct": False},
                    {"text": "Yeşil", "correct": True},
                    {"text": "Turuncu", "correct": False}
                ]
            },
            "investigate": {
                "id": "investigate",
                "text": "{{name}}, etrafı araştırırken gizli bir hazine sandığı buldun! Ama sandık kilitli. Ne yapacaksın?",
                "type": "choice",
                "background": "treasure",
                "options": [
                    {"label": "🔑 Anahtarı aramaya git", "next": "find_key"},
                    {"label": "🪄 Büyülü kelime dene", "next": "magic_word"},
                    {"label": "🏠 Kulübeye geri dön", "next": "cabin"}
                ]
            },
            "find_key": {
                "id": "find_key",
                "text": "{{name}}, anahtarı ararken bir matematik problemi ile karşılaştın!",
                "type": "quiz",
                "question": "Hazine koruması: '10 - 4 kaç eder?'",
                "background": "forest",
                "answers": [
                    {"text": "5", "correct": False},
                    {"text": "6", "correct": True},
                    {"text": "7", "correct": False}
                ]
            },
            "magic_word": {
                "id": "magic_word",
                "text": "{{name}}, büyülü kelimeyi doğru tahmin ettin! Sandık açıldı ve içinden parlak bir mücevher çıktı!",
                "type": "end",
                "background": "treasure"
            },
            "success": {
                "id": "success",
                "text": "Tebrikler {{name}}! Bulmacayı çözdün ve eve güvenle döndün. Sen gerçek bir kahramansın!",
                "type": "end",
                "background": "treasure"
            }
        }
    }

    # Uzay Macerası
    space_story = {
        "title": "Uzay Macerası",
        "description": "Uzay istasyonunda kaybolan astronot",
        "steps": {
            "start": {
                "id": "start",
                "text": "Astronot {{name}}! Uzay istasyonunda alarm çalıyor. Sistemde bir problem var. Ne yapacaksın?",
                "type": "choice",
                "background": "space",
                "options": [
                    {"label": "🚀 Kontrol odasına git", "next": "control_room"},
                    {"label": "🔧 Motor dairesini kontrol et", "next": "engine_room"},
                    {"label": "📡 İletişim merkezine git", "next": "communication"}
                ]
            },
            "control_room": {
                "id": "control_room",
                "text": "{{name}}, kontrol odasında bilgisayar bir matematik sorusu soruyor!",
                "type": "quiz",
                "question": "Bilgisayar: 'Uzay gemisinde 12 astronot var, 4'ü dışarı çıktı. İçeride kaç astronot kaldı?'",
                "background": "space",
                "answers": [
                    {"text": "8 astronot", "correct": True},
                    {"text": "9 astronot", "correct": False},
                    {"text": "7 astronot", "correct": False}
                ]
            },
            "engine_room": {
                "id": "engine_room",
                "text": "{{name}}, motor dairesinde robotla karşılaştın!",
                "type": "quiz",
                "question": "Robot: 'Hangi gezegen güneşe en yakın?'",
                "background": "space",
                "answers": [
                    {"text": "Venüs", "correct": False},
                    {"text": "Merkür", "correct": True},
                    {"text": "Mars", "correct": False}
                ]
            },
            "communication": {
                "id": "communication",
                "text": "Harika iş {{name}}! İletişim sistemini onardın ve Dünya ile bağlantı kurdun. Görevin tamamlandı!",
                "type": "end",
                "background": "space"
            },
            "success": {
                "id": "success",
                "text": "Mükemmel {{name}}! Uzay istasyonunu kurtardın. Sen gerçek bir uzay kahramanısın!",
                "type": "end",
                "background": "space"
            }
        }
    }

    # Pokemon Macerası
    pokemon_story = {
        "title": "Pokemon Eğitmeni Yolculuğu",
        "type": "pokemon",
        "description": "Pokemon dünyasında bir eğitmen olarak maceraya atıl! Pokemon'ları yakala, eğit ve en güçlü eğitmen ol!",
        "badges": {
            "gold": {
                "type": "pokemon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/pokemon_gold.png",
                "title": "Pokemon Ustası",
                "description": "Harika bir Pokemon eğitmeni oldun! Tüm zorlukların üstesinden geldin ve en güçlü eğitmen oldun!"
            },
            "silver": {
                "type": "pokemon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/pokemon_silver.png",
                "title": "Pokemon Eğitmeni",
                "description": "İyi bir Pokemon eğitmeni oldun! Çoğu zorluğu başarıyla aştın!"
            },
            "bronze": {
                "type": "pokemon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/pokemon_bronze.png",
                "title": "Pokemon Acemisi",
                "description": "Pokemon yolculuğuna başladın! Daha çok pratik yapmalısın!"
            },
            "basic": {
                "type": "pokemon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/pokemon_basic.png",
                "title": "Pokemon Meraklısı",
                "description": "Pokemon dünyasına hoş geldin! Daha çok öğrenmelisin!"
            }
        },
        "steps": {
            "start": {
                "id": "start",
                "text": "Merhaba {{name}}! Pokemon dünyasına hoş geldin! Profesör Oak'ın laboratuvarındasın. İlk Pokemon'unu seçmeye hazır mısın?",
                "type": "choice",
                "background": "lab",
                "options": [
                    {
                        "label": "🔥 Charmander'ı seç",
                        "next": "charmander_choice"
                    },
                    {
                        "label": "💧 Squirtle'ı seç",
                        "next": "squirtle_choice"
                    },
                    {
                        "label": "🌱 Bulbasaur'u seç",
                        "next": "bulbasaur_choice"
                    }
                ]
            },
            "charmander_choice": {
                "id": "charmander_choice",
                "text": "{{name}}, Charmander'ı seçtin! Bu ateş tipi Pokemon çok güçlü olacak. Şimdi ilk görevine hazır mısın?",
                "type": "quiz",
                "question": "Charmander hangi tür bir Pokemon'dur?",
                "background": "charmander",
                "answers": [
                    {
                        "text": "Ateş tipi",
                        "correct": True
                    },
                    {
                        "text": "Su tipi",
                        "correct": False
                    },
                    {
                        "text": "Toprak tipi",
                        "correct": False
                    }
                ]
            },
            "squirtle_choice": {
                "id": "squirtle_choice",
                "text": "{{name}}, Squirtle'ı seçtin! Bu su tipi Pokemon çok dayanıklı olacak. Şimdi ilk görevine hazır mısın?",
                "type": "quiz",
                "question": "Squirtle hangi tür bir Pokemon'dur?",
                "background": "squirtle",
                "answers": [
                    {
                        "text": "Ateş tipi",
                        "correct": False
                    },
                    {
                        "text": "Su tipi",
                        "correct": True
                    },
                    {
                        "text": "Toprak tipi",
                        "correct": False
                    }
                ]
            },
            "bulbasaur_choice": {
                "id": "bulbasaur_choice",
                "text": "{{name}}, Bulbasaur'u seçtin! Bu çim tipi Pokemon çok güçlü olacak. Şimdi ilk görevine hazır mısın?",
                "type": "quiz",
                "question": "Bulbasaur hangi tür bir Pokemon'dur?",
                "background": "bulbasaur",
                "answers": [
                    {
                        "text": "Ateş tipi",
                        "correct": False
                    },
                    {
                        "text": "Su tipi",
                        "correct": False
                    },
                    {
                        "text": "Çim tipi",
                        "correct": True
                    }
                ]
            },
            "first_battle": {
                "id": "first_battle",
                "text": "{{name}}, ormanda ilk Pokemon savaşına hazır mısın? Karşına bir yabani Pokemon çıktı!",
                "type": "choice",
                "background": "forest",
                "options": [
                    {
                        "label": "⚔️ Savaş",
                        "next": "battle_quiz"
                    },
                    {
                        "label": "🏃 Kaç",
                        "next": "run_away"
                    },
                    {
                        "label": "🎣 Pokemon yakala",
                        "next": "catch_pokemon"
                    }
                ]
            },
            "battle_quiz": {
                "id": "battle_quiz",
                "text": "{{name}}, savaş başladı! Pokemon'unun güçlü bir saldırı yapması için doğru komutu vermelisin!",
                "type": "quiz",
                "question": "Pokemon'unun en güçlü saldırısı hangisidir?",
                "background": "battle",
                "answers": [
                    {
                        "text": "Tackle",
                        "correct": False
                    },
                    {
                        "text": "Scratch",
                        "correct": False
                    },
                    {
                        "text": "Ember/Water Gun/Vine Whip",
                        "correct": True
                    }
                ]
            },
            "run_away": {
                "id": "run_away",
                "text": "{{name}}, kaçmayı denedin ama Pokemon seni takip ediyor! Ne yapacaksın?",
                "type": "choice",
                "background": "forest",
                "options": [
                    {
                        "label": "⚔️ Savaş",
                        "next": "battle_quiz"
                    },
                    {
                        "label": "🎣 Pokemon yakala",
                        "next": "catch_pokemon"
                    }
                ]
            },
            "catch_pokemon": {
                "id": "catch_pokemon",
                "text": "{{name}}, Pokemon'u yakalamak için doğru zamanı seçmelisin!",
                "type": "quiz",
                "question": "Pokemon'u yakalamak için en iyi zaman ne zamandır?",
                "background": "pokeball",
                "answers": [
                    {
                        "text": "Pokemon yorgunken",
                        "correct": True
                    },
                    {
                        "text": "Pokemon saldırırken",
                        "correct": False
                    },
                    {
                        "text": "Pokemon kaçarken",
                        "correct": False
                    }
                ]
            },
            "gym_challenge": {
                "id": "gym_challenge",
                "text": "{{name}}, ilk Pokemon salonuna vardın! Salon lideri Brock ile savaşmaya hazır mısın?",
                "type": "quiz",
                "question": "Brock hangi tür Pokemon'ları kullanır?",
                "background": "gym",
                "answers": [
                    {
                        "text": "Toprak ve Kaya tipi",
                        "correct": True
                    },
                    {
                        "text": "Ateş tipi",
                        "correct": False
                    },
                    {
                        "text": "Su tipi",
                        "correct": False
                    }
                ]
            },
            "victory": {
                "id": "victory",
                "text": "{{name}}, tebrikler! İlk Pokemon salonunu başarıyla tamamladın! Artık bir rozet kazandın!",
                "type": "end",
                "background": "badge"
            }
        }
    }

    # Elif'in Düşleri
    elif_story = {
        "title": "Elif'in Düşleri",
        "type": "cartoon",
        "description": "Elif'in hayal dünyasında maceraya atıl!",
        "badges": {
            "gold": {
                "type": "cartoon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/cartoon_gold.png",
                "title": "Hayal Ustası",
                "description": "Harika bir hayal gücün var! Tüm soruları doğru cevapladın."
            },
            "silver": {
                "type": "cartoon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/cartoon_silver.png",
                "title": "Hayal Perisi",
                "description": "Güzel hayaller kuruyorsun! Çoğu soruyu doğru cevapladın."
            },
            "bronze": {
                "type": "cartoon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/cartoon_bronze.png",
                "title": "Hayal Meraklısı",
                "description": "Hayal dünyasına hoş geldin! Daha çok hayal kurmalısın."
            },
            "basic": {
                "type": "cartoon",
                "image": "https://emreoztemiz-ai-ml.github.io/flutterweb/assets/badges/cartoon_basic.png",
                "title": "Hayal Acemisi",
                "description": "Hayal dünyasını keşfetmeye başladın! Daha çok pratik yapmalısın."
            }
        },
        "steps": {
            "start": {
                "id": "start",
                "text": "Merhaba {{name}}! Elif'in düş dünyasına hoş geldin! Burada her şey mümkün. Nereye gitmek istersin?",
                "type": "choice",
                "background": "dream",
                "options": [
                    {
                        "label": "🌈 Gökkuşağı Köprüsü",
                        "next": "rainbow"
                    },
                    {
                        "label": "🌙 Ay Kalesi",
                        "next": "moon_castle"
                    },
                    {
                        "label": "🌺 Çiçek Bahçesi",
                        "next": "flower_garden"
                    }
                ]
            },
            "rainbow": {
                "id": "rainbow",
                "text": "{{name}}, gökkuşağının üzerinde yürüyorsun! Renkler seninle konuşuyor. Hangi rengi dinlemek istersin?",
                "type": "quiz",
                "question": "Gökkuşağında kaç renk vardır?",
                "background": "rainbow",
                "answers": [
                    {
                        "text": "5 renk",
                        "correct": False
                    },
                    {
                        "text": "7 renk",
                        "correct": True
                    },
                    {
                        "text": "6 renk",
                        "correct": False
                    }
                ]
            },
            "moon_castle": {
                "id": "moon_castle",
                "text": "{{name}}, Ay Kalesi'ne vardın! Ay prensesi sana bir bilmece soruyor.",
                "type": "quiz",
                "question": "Ay neden bazen tam, bazen yarım görünür?",
                "background": "moon",
                "answers": [
                    {
                        "text": "Ay'ın Dünya etrafında dönmesi",
                        "correct": True
                    },
                    {
                        "text": "Ay'ın şekil değiştirmesi",
                        "correct": False
                    },
                    {
                        "text": "Ay'ın büyüyüp küçülmesi",
                        "correct": False
                    }
                ]
            },
            "flower_garden": {
                "id": "flower_garden",
                "text": "{{name}}, çiçekler seninle dans etmek istiyor! Hangi çiçekle dans edeceksin?",
                "type": "choice",
                "background": "garden",
                "options": [
                    {
                        "label": "🌹 Gül",
                        "next": "rose_dance"
                    },
                    {
                        "label": "🌻 Ayçiçeği",
                        "next": "sunflower_dance"
                    },
                    {
                        "label": "🌸 Kiraz Çiçeği",
                        "next": "cherry_dance"
                    }
                ]
            },
            "rose_dance": {
                "id": "rose_dance",
                "text": "{{name}}, gülle dans ederken bir matematik sorusu geldi aklına!",
                "type": "quiz",
                "question": "3 gül + 2 gül kaç gül eder?",
                "background": "garden",
                "answers": [
                    {
                        "text": "4 gül",
                        "correct": False
                    },
                    {
                        "text": "5 gül",
                        "correct": True
                    },
                    {
                        "text": "6 gül",
                        "correct": False
                    }
                ]
            },
            "sunflower_dance": {
                "id": "sunflower_dance",
                "text": "{{name}}, ayçiçeğiyle dans ederken güneş seni selamlıyor!",
                "type": "quiz",
                "question": "Güneş hangi yönden doğar?",
                "background": "garden",
                "answers": [
                    {
                        "text": "Doğu",
                        "correct": True
                    },
                    {
                        "text": "Batı",
                        "correct": False
                    },
                    {
                        "text": "Kuzey",
                        "correct": False
                    }
                ]
            },
            "cherry_dance": {
                "id": "cherry_dance",
                "text": "{{name}}, kiraz çiçeğiyle dans ederken rüzgar seni sallıyor!",
                "type": "quiz",
                "question": "Rüzgar hangi mevsimde daha çok eser?",
                "background": "garden",
                "answers": [
                    {
                        "text": "Yaz",
                        "correct": False
                    },
                    {
                        "text": "Kış",
                        "correct": False
                    },
                    {
                        "text": "İlkbahar",
                        "correct": True
                    }
                ]
            },
            "success": {
                "id": "success",
                "text": "{{name}}, harika bir düş macerası yaşadın! Artık uyanma vakti geldi. Seni tekrar bekleriz!",
                "type": "end",
                "background": "dream"
            }
        }
    }

    # JSON dosyalarını oluştur
    stories = [
        ("orman_macerasi.json", forest_story),
        ("uzay_macerasi.json", space_story),
        ("pokemon_adventure.json", pokemon_story),
        ("elifin_dusleri.json", elif_story)
    ]

    for filename, story_data in stories:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)
        print(f"📝 {filename} oluşturuldu")

def batch_encrypt_stories(password="BenimGizliKeyim"):
    """
    Klasördeki tüm JSON dosyalarını şifreler
    """
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if not json_files:
        print("❌ Hiç JSON dosyası bulunamadı!")
        return
    
    for json_file in json_files:
        try:
            encrypt_story(json_file, password)
        except Exception as e:
            print(f"❌ {json_file} şifrelenemedi: {e}")

if __name__ == "__main__":
    print("�� Hikaye Şifreleyici")
    print("=" * 30)
    
    # Örnek hikayeleri oluştur
    print("1️⃣ Örnek hikayeler oluşturuluyor...")
    create_sample_stories()
    
    print("\n2️⃣ Hikayeler şifreleniyor...")
    password = "BenimGizliKeyim"
    batch_encrypt_stories(password)
    
    print("\n✅ Tüm işlemler tamamlandı!")
    print("📁 .enc dosyalarını GitHub Pages'e yükleyebilirsiniz")
    
    # Manuel şifreleme örneği
    print("\n" + "="*50)
    print("Manuel kullanım örneği:")
    print("encrypt_story('hikayem.json', 'BenimGizliKeyim', 'hikayem.enc')")
    print("="*50)