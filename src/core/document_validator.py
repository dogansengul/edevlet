from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from ..config.config import config
from .human_behavior import HumanBehaviorSimulator

class DocumentValidator:
    """E-Devlet belge doğrulama işlemlerini yöneten sınıf"""
    
    def __init__(self, driver):
        self.driver = driver
        self.human = HumanBehaviorSimulator(driver)
    
    def navigate_to_validation_page(self):
        """Belge doğrulama sayfasına git"""
        print("Web sayfasına gidiliyor...")
        self.driver.get(config.EDEVLET_BELGE_DOGRULAMA_URL)
        self.human.random_sleep(2, 4)  # Sayfa yüklenme süresi
        print("Belge doğrulama sayfasına ulaşıldı.")
        
        # Sayfa yüklendikten sonra insan benzeri davranışlar sergile
        self.human.simulate_human_behavior()
    
    def enter_barcode(self, barcode=None):
        """Barkod numarasını gir"""
        if barcode is None:
            barcode = config.BARCODE_NUMBER
            
        try:
            print("Barkod numarası alanı bulunuyor...")
            barcode_input = self.human.wait_for_element(By.ID, "sorgulananBarkod")
            print("Barkod numarası alanı bulundu.")
            
            # İnsan benzeri yazma davranışı
            self.human.human_like_type(barcode_input, barcode)
            
            print("Devam Et butonuna tıklanıyor...")
            submit_button = self.human.wait_for_clickable(By.CSS_SELECTOR, "input.submitButton")
            self.human.human_like_click(submit_button)
            print("Devam Et butonuna tıklandı.")
            
            self.human.random_sleep(1, 2)
            
            # Hata mesajlarını kontrol et
            warning_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.warningContainer, div.errorContainer")
            if warning_containers:
                error_text = warning_containers[0].text
                print(f"Barkod hatası: {error_text}")
                
                # Hata türüne göre özel mesaj döndür
                if "Lütfen geçerli bir barkod numarası giriniz" in error_text:
                    return {
                        "success": False,
                        "error_type": "invalid_barcode_format",
                        "message": "Barkod numarası formatı geçersiz. Lütfen doğru formatı kullanın."
                    }
                elif "Girilen barkod numarası e-Devlet Kapısında tanımlı değildir" in error_text:
                    return {
                        "success": False,
                        "error_type": "barcode_not_registered",
                        "message": "Barkod numarası e-Devlet sisteminde tanımlı değil."
                    }
                else:
                    return {
                        "success": False,
                        "error_type": "barcode_error",
                        "message": f"Barkod hatası: {error_text}"
                    }
            
            # Hata yoksa devam et
            return True
        except Exception as e:
            print(f"Barkod girişi sırasında hata: {str(e)}")
            # Alternatif yöntem dene
            try:
                print("Alternatif barkod girişi yöntemi deneniyor...")
                barcode_input = self.driver.find_element(By.ID, "sorgulananBarkod")
                barcode_input.clear()
                barcode_input.send_keys(barcode)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                self.human.random_sleep(1, 2)
                
                # Hata mesajlarını kontrol et
                warning_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.warningContainer, div.errorContainer")
                if warning_containers:
                    error_text = warning_containers[0].text
                    print(f"Barkod hatası: {error_text}")
                    
                    if "Lütfen geçerli bir barkod numarası giriniz" in error_text:
                        return {
                            "success": False,
                            "error_type": "invalid_barcode_format",
                            "message": "Barkod numarası formatı geçersiz. Lütfen doğru formatı kullanın."
                        }
                    elif "Girilen barkod numarası e-Devlet Kapısında tanımlı değildir" in error_text:
                        return {
                            "success": False,
                            "error_type": "barcode_not_registered",
                            "message": "Barkod numarası e-Devlet sisteminde tanımlı değil."
                        }
                    else:
                        return {
                            "success": False,
                            "error_type": "barcode_error",
                            "message": f"Barkod hatası: {error_text}"
                        }
                
                return True
            except Exception as alt_e:
                print(f"Alternatif barkod girişi sırasında hata: {str(alt_e)}")
                return {
                    "success": False,
                    "error_type": "barcode_input_error",
                    "message": f"Barkod girişi sırasında teknik hata: {str(alt_e)}"
                }
    
    def enter_tc_kimlik_no(self, tc_kimlik_no=None):
        """TC Kimlik numarasını gir"""
        if tc_kimlik_no is None:
            tc_kimlik_no = config.TC_KIMLIK_NO
            
        try:
            print("TC Kimlik No alanı bulunuyor...")
            # Sayfanın yüklenmesi için bekle
            self.human.random_sleep(5, 7)
            
            # URL kontrolü yap - doğrulama sayfasında olduğumuzdan emin olalım
            current_url = self.driver.current_url
            print(f"Mevcut URL: {current_url}")
            
            # Sayfa kaynağını yazdır (hata ayıklama için)
            page_source = self.driver.page_source
            if "kimlik" in page_source.lower() or "TC" in page_source:
                print("Sayfa içeriğinde TC Kimlik alanı bulunabilir.")
            else:
                print("UYARI: Sayfa içeriğinde TC Kimlik alanı bulunamadı.")
                
            # Sayfayı yenilemek gerekebilir
            if "dogrulama" in current_url and not "kimlik" in page_source.lower():
                print("Sayfa yenileniyor...")
                self.driver.refresh()
                self.human.random_sleep(3, 5)
            
            # Tüm form alanlarını ve etiketlerini yazdır
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            print(f"Sayfada {len(all_inputs)} input alanı bulundu.")
            for i, inp in enumerate(all_inputs):
                print(f"Input #{i}: id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, type={inp.get_attribute('type')}")
                
            # Form bulmayı dene
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"Sayfada {len(forms)} form bulundu.")
            
            # Esnek element arama stratejisi - birçok seçiciyi dene
            tc_input = None
            
            try:
                # Sayfa başlıklarını kontrol ederek doğru sayfada olduğumuzdan emin ol
                headers = self.driver.find_elements(By.TAG_NAME, "h1")
                for header in headers:
                    if "doğrulama" in header.text.lower():
                        print(f"Doğrulama sayfası başlığı bulundu: {header.text}")
                
                # Önce TC Kimlik No için CSS seçicileri dene
                selectors = [
                    "input[name='tckn']",
                    "input[id='tckn']",
                    "input[name*='kimlik']",
                    "input[id*='kimlik']",
                    "input[placeholder*='Kimlik']",
                    "input.text:not(#sorgulananBarkod)",
                    "input[type='text']:not(#sorgulananBarkod)"
                ]
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"Seçici '{selector}' ile {len(elements)} element bulundu.")
                        tc_input = elements[0]
                        break
                
                # CSS seçiciler başarısız olduysa label içeriğine göre ara
                if not tc_input:
                    labels = self.driver.find_elements(By.TAG_NAME, "label")
                    for label in labels:
                        if "kimlik" in label.text.lower() or "TC" in label.text:
                            print(f"TC Kimlik ile ilgili label bulundu: {label.text}")
                            label_for = label.get_attribute("for")
                            if label_for:
                                tc_input = self.driver.find_element(By.ID, label_for)
                                break
                
                # Hala bulunamadıysa
                if not tc_input:
                    # Barkod alanı dışındaki ilk text input'u dene
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']:not(#sorgulananBarkod)")
                    if text_inputs:
                        tc_input = text_inputs[0]
                        print(f"Alternatif text input bulundu: id={tc_input.get_attribute('id')}")
            
            except Exception as search_error:
                print(f"TC Kimlik No alanı ararken hata: {search_error}")
                # Ekran görüntüsü al
                screenshot_path = f"src/screenshots/tc_search_error_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Hata anında ekran görüntüsü: {screenshot_path}")
            
            # Eğer hala input bulunamadıysa son çare olarak JavaScript ile oluştur
            if not tc_input:
                print("TC Kimlik No alanı bulunamadı, form analiz ediliyor...")
                form_html = self.driver.find_element(By.TAG_NAME, "form").get_attribute("innerHTML")
                if "ikinciAlan" in form_html:
                    print("Form içinde 'ikinciAlan' ID'si bulundu, JavaScript ile değer ataması deneniyor...")
                    self.driver.execute_script(f"document.getElementById('ikinciAlan').value = '{tc_kimlik_no}';")
                    self.human.random_sleep(1, 2)
                    tc_input = self.driver.find_element(By.ID, "ikinciAlan")
                else:
                    # Son çare: CSS seçici kullanarak 1. adımdan sonraki input
                    print("Son çare: Devam butonundan sonraki ilk input aranıyor...")
                    tc_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            
            if not tc_input:
                raise Exception("TC Kimlik No için input alanı bulunamadı.")
            
            print(f"TC Kimlik No alanı bulundu! ID: {tc_input.get_attribute('id')}, Name: {tc_input.get_attribute('name')}")
            
            # Görünür olana kadar bekle ve scroll yap
            self.human.scroll_to_element(tc_input)
            self.human.random_sleep(1, 2)
            
            # İnsan benzeri yazma davranışıyla doldur
            tc_input.click()
            tc_input.clear()
            self.human.human_like_type(tc_input, tc_kimlik_no)
            print(f"TC Kimlik No insan benzeri davranışla girildi: {tc_kimlik_no}")
            
            # Sayfa URL'sini ve başlığını kaydet (sayfa değişikliğini kontrol etmek için)
            before_url = self.driver.current_url
            before_title = self.driver.title
            
            # Formun gönderilmeden önceki içeriğini kaydet (hata tespiti için)
            before_form_error = len(self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored"))
            before_page_content = self.driver.page_source
            
            # Devam Et butonunu kesin CSS seçiciyle bul
            print("Devam Et butonunu arıyorum...")
            # Tam ve kesin CSS seçici kullan
            submit_button = None
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton[name='btn'][type='submit'][value='Devam Et']")
                print("Devam Et butonu tam CSS seçiciyle bulundu")
            except:
                try:
                    # Daha esnek bir seçici dene
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton[value='Devam Et']")
                    print("Devam Et butonu esnek CSS seçiciyle bulundu")
                except:
                    try:
                        # En basit seçici
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                        print("Devam Et butonu genel CSS seçiciyle bulundu")
                    except:
                        print("Devam Et butonu CSS seçicilerle bulunamadı, tüm butonları kontrol ediyorum")
                        # Tüm submit butonlarını bul ve içlerinden "Devam Et" değerine sahip olanı seç
                        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                        for btn in all_buttons:
                            if btn.get_attribute("value") == "Devam Et":
                                submit_button = btn
                                print("Devam Et butonu tüm butonlar içinden bulundu")
                                break
            
            if not submit_button:
                # Buton bulunamadıysa ekran görüntüsü al ve form göndermeyi dene
                screenshot_path = f"src/screenshots/submit_button_not_found_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"Buton bulunamadı! Ekran görüntüsü: {screenshot_path}")
                
                # Form göndermeyi dene
                form = self.driver.find_element(By.TAG_NAME, "form")
                print("Form doğrudan submit ediliyor...")
                self.driver.execute_script("arguments[0].submit();", form)
            else:
                # Butonu görünür hale getir
                self.human.scroll_to_element(submit_button)
                self.human.random_sleep(1, 2)
                
                # Buton tıklanabilir mi kontrol et
                if submit_button.is_enabled() and submit_button.is_displayed():
                    print("Buton tıklanabilir durumda, tıklanıyor...")
                    # Ekran görüntüsü al (hata ayıklama için)
                    self.driver.save_screenshot(f"src/screenshots/before_click_{int(time.time())}.png")
                    
                    # Önce standart tıklama dene
                    try:
                        submit_button.click()
                        print("Butona standart yöntemle tıklandı")
                    except Exception as click_error:
                        print(f"Standart tıklama hatası: {click_error}")
                        print("JavaScript ile tıklama deneniyor...")
                        try:
                            self.driver.execute_script("arguments[0].click();", submit_button)
                            print("Butona JavaScript ile tıklandı")
                        except Exception as js_error:
                            print(f"JavaScript ile tıklama hatası: {js_error}")
                            print("Son çare: Form doğrudan submit ediliyor...")
                            try:
                                form = self.driver.find_element(By.TAG_NAME, "form")
                                self.driver.execute_script("arguments[0].submit();", form)
                                print("Form doğrudan submit edildi")
                            except Exception as form_error:
                                print(f"Form submit hatası: {form_error}")
                                raise Exception("Hiçbir şekilde form gönderilemedi")
                else:
                    print("Buton tıklanabilir durumda değil!")
                    self.driver.save_screenshot(f"src/screenshots/button_not_clickable_{int(time.time())}.png")
                    raise Exception("Buton tıklanabilir durumda değil")
            
            # Kısa bir bekleyiş (form işlensin diye)
            self.human.random_sleep(2, 3)
            
            # Sayfada TC Kimlik No hatası oluştu mu kontrol et (URL değişmeden önce)
            tc_error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
            if tc_error_elements:
                try:
                    error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                    if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                        print(f"TC Kimlik No hatası tespit edildi: {error_message}")
                        # Ekran görüntüsü al
                        self.driver.save_screenshot(f"src/screenshots/tc_kimlik_error_{int(time.time())}.png")
                        return {
                            "success": False,
                            "error_type": "invalid_tc_kimlik_format",
                            "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                        }
                except:
                    pass
            
            # Sayfa içeriği değişti mi kontrol et
            after_page_content = self.driver.page_source
            if after_page_content != before_page_content:
                print("Sayfa içeriği değişti, form işlendi")
                
                # Yeni hata kontrolü
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored, div.warningContainer, div.errorContainer")
                if error_elements:
                    try:
                        error_message = error_elements[0].text
                        print(f"Form gönderimi sonrası hata: {error_message}")
                        
                        if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                            return {
                                "success": False,
                                "error_type": "invalid_tc_kimlik_format",
                                "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                            }
                    except:
                        pass
            
            # Sayfa değişikliğini kontrol et
            wait_time = 10  # 10 saniye bekle
            print(f"Sayfa değişikliği bekleniyor... ({wait_time} saniye)")
            for _ in range(wait_time):
                time.sleep(1)
                current_url = self.driver.current_url
                current_title = self.driver.title
                
                # URL değişimini veya sayfa başlık değişimini kontrol et
                if current_url != before_url or current_title != before_title:
                    print(f"Sayfa değişikliği tespit edildi! Yeni URL: {current_url}")
                    # Ekran görüntüsü al
                    self.driver.save_screenshot(f"src/screenshots/after_page_change_{int(time.time())}.png")
                    break
                
                # Her saniye kontroller:
                # 1. Form üzerinde hata mesajı olup olmadığını kontrol et
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
                if len(error_elements) > before_form_error:
                    try:
                        error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                        print(f"Form gönderimi sonrası TC Kimlik No hatası: {error_message}")
                        if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                            # TC Kimlik No hatalı
                            self.driver.save_screenshot(f"src/screenshots/tc_kimlik_error_{int(time.time())}.png")
                            return {
                                "success": False,
                                "error_type": "invalid_tc_kimlik_format",
                                "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                            }
                    except:
                        # ID bulunamasa da hata olabilir, içeriği kontrol et
                        error_text = error_elements[0].text
                        print(f"Form hatası: {error_text}")
                        if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_text:
                            return {
                                "success": False,
                                "error_type": "invalid_tc_kimlik_format",
                                "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                            }
                
                # 2. Sayfa içeriği değişti mi kontrol et
                current_page_content = self.driver.page_source
                if current_page_content != before_page_content:
                    print("Sayfa içeriği değişti, işlem devam ediyor...")
            else:
                # For döngüsü break ile kırılmazsa ve hata tespit edilmediyse buraya gelir
                print("Sayfa değişikliği tespit edilemedi! Tıklama başarısız olabilir.")
                self.driver.save_screenshot(f"src/screenshots/no_page_change_{int(time.time())}.png")
                
                # Son bir kez daha hata kontrolü yap
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
                if error_elements:
                    try:
                        error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                        print(f"Son kontrol: TC Kimlik No hatası: {error_message}")
                        
                        if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                            return {
                                "success": False,
                                "error_type": "invalid_tc_kimlik_format",
                                "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                            }
                    except:
                        pass
                
                # Hata tespit edilmediyse ve sayfa değişmemişse, tekrar tıklamayı dene
                try:
                    print("Tekrar tıklama deneniyor...")
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton[value='Devam Et']")
                    self.driver.execute_script("arguments[0].click();", submit_button)
                    time.sleep(5)  # Sayfa değişikliği için biraz daha bekle
                    
                    # Tekrar kontrol et
                    if self.driver.current_url != before_url:
                        print("İkinci denemede sayfa değişikliği tespit edildi!")
                    else:
                        # Son bir kontrol daha
                        error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored")
                        if error_elements:
                            try:
                                error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                                print(f"İkinci tıklamadan sonra TC Kimlik No hatası: {error_message}")
                                
                                if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                                    return {
                                        "success": False,
                                        "error_type": "invalid_tc_kimlik_format",
                                        "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                                    }
                            except:
                                pass
                        
                        raise Exception("İkinci tıklama denemesi de başarısız oldu, sayfa değişmedi")
                except Exception as retry_error:
                    print(f"Tekrar tıklama hatası: {retry_error}")
                    raise Exception("Sayfa değişmedi, tıklama başarısız")
            
            # TC Kimlik No doğrulama kontrolü
            validation_result = self.check_tc_kimlik_validation()
            return validation_result
        except Exception as e:
            print(f"TC Kimlik No girişi sırasında hata: {str(e)}")
            screenshot_path = f"src/screenshots/tc_error_{int(time.time())}.png"
            print(f"Hata ekran görüntüsü kaydediliyor: {screenshot_path}")
            try:
                self.driver.save_screenshot(screenshot_path)
            except:
                print("Ekran görüntüsü alınamadı")
                
            return {
                "success": False,
                "error_type": "input_error",
                "message": f"TC Kimlik No girişi yapılamadı: {str(e)}"
            }
    
    def check_tc_kimlik_validation(self):
        """TC Kimlik numarası doğrulama sonucunu kontrol et"""
        try:
            # Hata mesajı içeren div'i kontrol et
            error_div = self.driver.find_elements(By.CSS_SELECTOR, "div.formRow.required.errored, div.warningContainer, div.errorContainer")
            
            if error_div:
                # Hata mesajını bul
                try:
                    error_message = self.driver.find_element(By.ID, "ikinciAlan-error").text
                except:
                    # Eğer belirli ID ile bulunamazsa, genel hata mesajını al
                    error_message = error_div[0].text
                
                print(f"TC Kimlik No Hatası: {error_message}")
                
                # Hata türüne göre özel mesaj döndür
                if "Lütfen geçerli bir T.C. Kimlik No giriniz" in error_message:
                    return {
                        "success": False,
                        "error_type": "invalid_tc_kimlik_format",
                        "message": "Geçersiz TC kimlik numarası. Lütfen doğru TC kimlik numarasını giriniz."
                    }
                else:
                    return {
                        "success": False,
                        "error_type": "tc_kimlik_error",
                        "message": error_message
                    }
            
            # Hata yoksa başarılı
            return {
                "success": True
            }
            
        except Exception as e:
            print(f"TC Kimlik No doğrulama kontrolünde hata: {str(e)}")
            return {
                "success": False,
                "error_type": "unknown_error",
                "message": f"TC Kimlik No doğrulama kontrolünde beklenmeyen bir hata oluştu: {str(e)}"
            }
    
    def accept_terms(self):
        """Onay kutusunu işaretle ve devam et"""
        try:
            print("Checkbox bulunuyor ve işaretleniyor...")
            # Sayfanın tamamen yüklenmesini bekle
            self.human.random_sleep(2, 3)
            
            # Önce sayfayı yukarı kaydır
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human.random_sleep(1, 2)
            
            # Checkbox'ı bulmayı dene
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "chkOnay"))
            )
            
            # Checkbox'a scroll yap
            self.human.scroll_to_element(checkbox)
            self.human.random_sleep(1, 2)
            
            # JavaScript ile tıkla (daha güvenilir)
            self.driver.execute_script("arguments[0].click();", checkbox)
            print("Checkbox işaretlendi.")
            
            print("Devam Et butonuna tekrar tıklanıyor...")
            self.human.random_sleep(1, 2)
            
            # Submit butonunu bul
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.submitButton"))
            )
            
            # Butona scroll yap
            self.human.scroll_to_element(submit_button)
            self.human.random_sleep(1, 2)
            
            # JavaScript ile tıkla
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("Devam Et butonuna tekrar tıklandı.")
            
            self.human.random_sleep(2, 4)
            return True
        except Exception as e:
            print(f"Onay işlemi sırasında hata: {str(e)}")
            # Alternatif yöntem dene
            try:
                print("Alternatif onay işlemi yöntemi deneniyor...")
                # Sayfanın tamamen yüklenmesini bekle
                self.human.random_sleep(3, 5)
                
                # Checkbox'ı farklı yöntemlerle bulmayı dene
                try:
                    checkbox = self.driver.find_element(By.ID, "chkOnay")
                except:
                    try:
                        checkbox = self.driver.find_element(By.NAME, "chkOnay")
                    except:
                        checkbox = self.driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                
                # JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", checkbox)
                self.human.random_sleep(1, 2)
                
                # Submit butonunu farklı yöntemlerle bulmayı dene
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, "input.submitButton")
                except:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    except:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                
                # JavaScript ile tıkla
                self.driver.execute_script("arguments[0].click();", submit_button)
                
                self.human.random_sleep(2, 4)
                return True
            except Exception as alt_e:
                print(f"Alternatif onay işlemi sırasında hata: {str(alt_e)}")
                return False
    
    def check_invalid_barcode_warning(self):
        """Geçersiz barkod uyarısını kontrol et"""
        try:
            warning_container = self.driver.find_elements(By.CSS_SELECTOR, "div.warningContainer[role='alert']")
            if warning_container:
                warning_text = warning_container[0].find_element(By.TAG_NAME, "span").text
                print(f"Geçersiz barkod uyarısı: {warning_text}")
                return True
            return False
        except Exception as e:
            print(f"Barkod uyarı kontrolünde hata: {str(e)}")
            return False

    def is_validation_successful(self):
        """Doğrulama işleminin başarılı olup olmadığını kontrol et"""
        try:
            # Önce geçersiz barkod uyarısını kontrol et
            if self.check_invalid_barcode_warning():
                print("Geçersiz barkod numarası tespit edildi!")
                return {
                    "success": False,
                    "error_type": "invalid_barcode",
                    "message": "Geçersiz barkod numarası tespit edildi."
                }
                
            # URL'yi kontrol et
            current_url = self.driver.current_url
            
            # Hata sayfasını kontrol et
            if "hata=sayfasi" in current_url:
                error_message = "Belge doğrulama hatası"
                try:
                    error_container = self.driver.find_element(By.CSS_SELECTOR, "div.errorContainer, div.warningContainer")
                    if error_container:
                        error_message = error_container.text
                except:
                    pass
                
                print(f"Doğrulama hatası: {error_message}")
                
                # Doğrulama kodu sistem kayıtlarında bulunamadı hatası
                if "Doğrulama kodu sistem kayıtlarında bulunamadı" in error_message:
                    return {
                        "success": False,
                        "error_type": "barcode_not_found",
                        "message": "Doğrulama kodu sistem kayıtlarında bulunamadı. Barkod geçerli fakat sistemde kayıtlı değil."
                    }
                else:
                    return {
                        "success": False,
                        "error_type": "validation_error",
                        "message": error_message
                    }
            
            # Belge gösterme sayfasını kontrol et
            if "belge=goster" in current_url or "belge-dogrulama" in current_url:
                print("İşlem başarılı! Sonuç sayfasına ulaşıldı.")
                return {
                    "success": True
                }
            else:
                print(f"Beklenmedik bir durum oluştu. URL: {current_url}")
                return {
                    "success": False,
                    "error_type": "unexpected_state",
                    "message": f"Beklenmedik bir sayfa durumu. URL: {current_url}"
                }
        except Exception as e:
            print(f"Doğrulama kontrolü sırasında hata: {str(e)}")
            return {
                "success": False,
                "error_type": "validation_check_error",
                "message": f"Doğrulama kontrolü sırasında teknik hata: {str(e)}"
            }
    
    def get_download_link(self):
        """Dosya indirme bağlantısını bul"""
        try:
            download_link = self.human.wait_for_element(By.CSS_SELECTOR, "a.download")
            download_link_url = download_link.get_attribute("href")
            print(f"Dosya indirme bağlantısı bulundu: {download_link_url}")
            return download_link, download_link_url
        except Exception as e:
            print(f"Dosya indirme bağlantısında hata: {str(e)}")
            return None, None 