# Harmonogram pracy inżynierskiej  
## Od 1 lipca do 1 września 2026

**Temat projektu:** aplikacja pobierająca dane giełdowe przez API, analizująca je z użyciem filtru Kalmana i sterowania predykcyjnego MPC, a następnie generująca dla użytkownika decyzje inwestycyjne.

**Główny cel:**  
Do **1 sierpnia 2026** gotowa ma być cała część praktyczna, czyli działająca aplikacja, testy, wykresy i wyniki.  
Od **2 sierpnia do 1 września 2026** priorytetem jest pisanie pracy, poprawki, formatowanie i przygotowanie wersji końcowej.

---

## Najważniejsze deadline’y

| Data | Cel |
|---|---|
| 06.07 | Gotowy moduł pobierania i przygotowania danych giełdowych |
| 13.07 | Gotowy filtr Kalmana |
| 21.07 | Gotowe sterowanie predykcyjne MPC i logika decyzji |
| 27.07 | Gotowa aplikacja użytkownika |
| 01.08 | Zamknięta część praktyczna: kod, wyniki, wykresy, README |
| 15.08 | Napisana około połowa pracy |
| 22.08 | Napisana całość merytoryczna pracy |
| 31.08 | Gotowa wersja końcowa |
| 01.09 | Ostateczna kontrola i przygotowanie do oddania |

---

# Lipiec — wykonanie aplikacji

## Tydzień 1: Dane giełdowe i przygotowanie projektu  
### 1 lipca – 6 lipca

**Cel tygodnia:** aplikacja potrafi pobrać dane giełdowe z API, oczyścić je i przygotować do dalszej analizy.

### 01.07 — Środa
- [ ] Utworzenie repozytorium projektu.
- [ ] Przygotowanie struktury katalogów.
- [ ] Wybór API do danych giełdowych.
- [ ] Implementacja podstawowego pobierania danych.
- [ ] Sprawdzenie, jakie dane są dostępne: cena 
otwarcia, zamknięcia, maksimum, minimum, wolumen.
- [ ] Design UI

### 02.07 — Czwartek
- [ ] Obsługa błędów API.
- [ ] Obsługa limitów zapytań.
- [ ] Obsługa brakujących danych.
- [ ] Przygotowanie funkcji pobierającej dane dla wybranej spółki lub indeksu.

### 03.07 — Piątek
- [ ] Czyszczenie danych.
- [ ] Konwersja dat.
- [ ] Usunięcie lub uzupełnienie braków.
- [ ] Przygotowanie danych wejściowych dla filtru Kalmana.

### 04.07 — Sobota
- [ ] Dodanie zapisu danych lokalnie.
- [ ] Wybór formatu zapisu: CSV, SQLite lub cache w plikach.
- [ ] Test ponownego uruchomienia aplikacji bez konieczności każdorazowego pobierania tych samych danych.

### 05.07 — Niedziela
- [ ] Testy pobierania danych dla kilku instrumentów finansowych.
- [ ] Sprawdzenie poprawności danych.
- [ ] Przygotowanie pierwszych prostych wykresów ceny.

### 06.07 — Poniedziałek
- [ ] Uporządkowanie modułu danych.
- [ ] Komentarze w kodzie.
- [ ] Krótki opis modułu danych do późniejszego rozdziału pracy.
- [ ] Backup kodu.

**Efekt tygodnia:** gotowy moduł API i przygotowania danych.

---

## Tydzień 2: Filtr Kalmana  
### 7 lipca – 13 lipca

**Cel tygodnia:** aplikacja wykorzystuje filtr Kalmana do wygładzania danych i estymacji trendu ceny.

### 07.07 — Wtorek
- [ ] Przypomnienie teorii filtru Kalmana.
- [ ] Zapisanie modelu matematycznego.
- [ ] Określenie, co jest stanem systemu, a co pomiarem.
- [ ] Przygotowanie notatek do rozdziału teoretycznego.

### 08.07 — Środa
- [ ] Implementacja podstawowego filtru Kalmana.
- [ ] Test filtru na prostych danych.
- [ ] Sprawdzenie poprawności obliczeń.

### 09.07 — Czwartek
- [ ] Dobór parametrów filtru.
- [ ] Ustalenie szumu procesu.
- [ ] Ustalenie szumu pomiaru.
- [ ] Test wpływu parametrów na wynik.

### 10.07 — Piątek
- [ ] Zastosowanie filtru do rzeczywistych danych giełdowych.
- [ ] Porównanie ceny rzeczywistej z wartością estymowaną.
- [ ] Przygotowanie wykresu: cena rzeczywista vs filtr Kalmana.

### 11.07 — Sobota
- [ ] Dodanie wizualizacji do aplikacji.
- [ ] Oznaczenie na wykresie trendu i odchyleń.
- [ ] Zapis wykresów do plików.

### 12.07 — Niedziela
- [ ] Testy filtru dla różnych spółek lub indeksów.
- [ ] Testy dla różnych zakresów dat.
- [ ] Spisanie obserwacji.

### 13.07 — Poniedziałek
- [ ] Uporządkowanie kodu filtru Kalmana.
- [ ] Dodanie komentarzy.
- [ ] Przygotowanie opisu działania filtru do pracy.
- [ ] Backup kodu i wykresów.

**Efekt tygodnia:** gotowy filtr Kalmana oraz wykresy do pracy.

---

## Tydzień 3: Sterowanie predykcyjne MPC i decyzje inwestycyjne  
### 14 lipca – 21 lipca

**Cel tygodnia:** aplikacja generuje decyzje inwestycyjne na podstawie predykcji i ograniczeń.

### 14.07 — Wtorek
- [ ] Zdefiniowanie problemu sterowania predykcyjnego.
- [ ] Określenie stanu systemu.
- [ ] Określenie zmiennych decyzyjnych.
- [ ] Określenie horyzontu predykcji.

### 15.07 — Środa
- [ ] Zdefiniowanie funkcji celu.
- [ ] Uwzględnienie maksymalizacji potencjalnego zysku.
- [ ] Uwzględnienie minimalizacji ryzyka.
- [ ] Dodanie kary za zbyt częste transakcje.

### 16.07 — Czwartek
- [ ] Implementacja prostego modelu predykcyjnego.
- [ ] Połączenie predykcji z danymi z filtru Kalmana.
- [ ] Test działania na danych historycznych.

### 17.07 — Piątek
- [ ] Implementacja logiki decyzji:
  - [ ] kup,
  - [ ] sprzedaj,
  - [ ] trzymaj,
  - [ ] ostrzeżenie o ryzyku.
- [ ] Dodanie krótkiego uzasadnienia decyzji dla użytkownika.

### 18.07 — Sobota
- [ ] Dodanie ograniczeń:
  - [ ] maksymalna pozycja,
  - [ ] minimalny próg zmiany ceny,
  - [ ] ograniczenie ryzyka,
  - [ ] opcjonalny limit liczby transakcji.
- [ ] Testy działania ograniczeń.

### 19.07 — Niedziela
- [ ] Backtesting strategii na danych historycznych.
- [ ] Obliczenie stopy zwrotu.
- [ ] Obliczenie liczby transakcji.
- [ ] Obliczenie prostych miar ryzyka.

### 20.07 — Poniedziałek
- [ ] Porównanie działania MPC z prostą strategią bazową.
- [ ] Strategia bazowa: buy & hold lub średnia krocząca.
- [ ] Przygotowanie tabeli porównawczej wyników.

### 21.07 — Wtorek
- [ ] Uporządkowanie kodu MPC.
- [ ] Komentarze w kodzie.
- [ ] Spisanie wyników i obserwacji.
- [ ] Backup kodu, tabel i wykresów.

**Efekt tygodnia:** gotowe MPC i moduł decyzji inwestycyjnych.

---

## Tydzień 4: Aplikacja użytkownika  
### 22 lipca – 27 lipca

**Cel tygodnia:** połączyć wszystkie moduły w jedną działającą aplikację.

### 22.07 — Środa
- [ ] Połączenie modułów:
  - [ ] API,
  - [ ] przetwarzanie danych,
  - [ ] filtr Kalmana,
  - [ ] MPC,
  - [ ] moduł decyzji.
- [ ] Test przepływu danych od pobrania do wygenerowania decyzji.

### 23.07 — Czwartek
- [ ] Stworzenie prostego interfejsu użytkownika.
- [ ] Dodanie wyboru spółki lub indeksu.
- [ ] Dodanie wyboru zakresu dat.
- [ ] Dodanie przycisku uruchamiającego analizę.

### 24.07 — Piątek
- [ ] Dodanie wykresów do aplikacji.
- [ ] Wykres ceny rzeczywistej.
- [ ] Wykres estymacji filtru Kalmana.
- [ ] Oznaczenie decyzji kup/sprzedaj/trzymaj na wykresie.

### 25.07 — Sobota
- [ ] Dodanie panelu rekomendacji.
- [ ] Wyświetlanie decyzji dla użytkownika.
- [ ] Wyświetlanie krótkiego uzasadnienia.
- [ ] Wyświetlanie poziomu ryzyka.

### 26.07 — Niedziela
- [ ] Dodanie raportu wyników.
- [ ] Stopa zwrotu.
- [ ] Liczba transakcji.
- [ ] Porównanie z benchmarkiem.
- [ ] Eksport wyników do pliku.

### 27.07 — Poniedziałek
- [ ] Pełny test aplikacji od zera.
- [ ] Poprawki błędów.
- [ ] Uporządkowanie widoku aplikacji.
- [ ] Przygotowanie screenów aplikacji.

**Efekt tygodnia:** gotowa działająca aplikacja.

---

## Tydzień 5: Testy, wyniki i zamknięcie części praktycznej  
### 28 lipca – 1 sierpnia

**Cel tygodnia:** zamknąć kod, wyniki i materiały do pracy.

### 28.07 — Wtorek
- [ ] Testy na minimum 3 instrumentach finansowych.
- [ ] Testy na różnych zakresach czasu.
- [ ] Zapis wyników.

### 29.07 — Środa
- [ ] Przygotowanie tabel z wynikami.
- [ ] Porównanie strategii MPC z benchmarkiem.
- [ ] Sprawdzenie, czy wyniki są logiczne i możliwe do opisania.

### 30.07 — Czwartek
- [ ] Przygotowanie wykresów do pracy:
  - [ ] dane rzeczywiste,
  - [ ] estymacja Kalmana,
  - [ ] decyzje MPC,
  - [ ] porównanie wyników.
- [ ] Eksport wykresów w dobrej jakości.

### 31.07 — Piątek
- [ ] Ostateczne poprawki kodu.
- [ ] Komentarze w najważniejszych miejscach.
- [ ] Przygotowanie pliku README.
- [ ] Uporządkowanie repozytorium.

### 01.08 — Sobota
- [ ] Zamknięcie części praktycznej.
- [ ] Backup kodu.
- [ ] Backup danych.
- [ ] Backup wykresów.
- [ ] Backup wyników.
- [ ] Spisanie krótkiego podsumowania działania aplikacji.

**Efekt do 1 sierpnia:** gotowy projekt praktyczny. Od tego momentu nie dodawać dużych nowych funkcji.

---

# Sierpień — pisanie pracy

## Tydzień 6: Wstęp i teoria  
### 2 sierpnia – 8 sierpnia

**Cel tygodnia:** napisać wstęp i rozdział teoretyczny.

### 02.08 — Niedziela
- [ ] Przygotowanie pełnego spisu treści.
- [ ] Ustalenie struktury rozdziałów.
- [ ] Ustalenie listy rysunków i tabel, które będą potrzebne.

### 03.08 — Poniedziałek
- [ ] Pisanie wstępu.
- [ ] Opis problemu.
- [ ] Opis motywacji.
- [ ] Opis celu pracy.

### 04.08 — Wtorek
- [ ] Opis zakresu pracy.
- [ ] Opis założeń projektu.
- [ ] Opis ograniczeń rozwiązania.

### 05.08 — Środa
- [ ] Rozdział teoretyczny: rynki finansowe.
- [ ] Opis danych giełdowych.
- [ ] Opis szeregów czasowych.

### 06.08 — Czwartek
- [ ] Rozdział teoretyczny: filtr Kalmana.
- [ ] Opis modelu.
- [ ] Opis etapów predykcji i korekcji.
- [ ] Dodanie wzorów.

### 07.08 — Piątek
- [ ] Rozdział teoretyczny: sterowanie predykcyjne MPC.
- [ ] Opis funkcji celu.
- [ ] Opis ograniczeń.
- [ ] Opis horyzontu predykcji.

### 08.08 — Sobota
- [ ] Uzupełnienie bibliografii.
- [ ] Poprawki w rozdziale teoretycznym.
- [ ] Sprawdzenie spójności pojęć.

**Efekt tygodnia:** napisany wstęp i rozdział teoretyczny.

---

## Tydzień 7: Projekt i implementacja aplikacji  
### 9 sierpnia – 15 sierpnia

**Cel tygodnia:** opisać, jak została zaprojektowana i zaimplementowana aplikacja.

### 09.08 — Niedziela
- [ ] Opis wymagań funkcjonalnych.
- [ ] Opis wymagań niefunkcjonalnych.
- [ ] Opis przypadków użycia.

### 10.08 — Poniedziałek
- [ ] Opis architektury systemu.
- [ ] Diagram przepływu danych.
- [ ] Opis modułów aplikacji.

### 11.08 — Wtorek
- [ ] Opis modułu pobierania danych z API.
- [ ] Opis struktury danych.
- [ ] Opis czyszczenia danych.

### 12.08 — Środa
- [ ] Opis implementacji filtru Kalmana.
- [ ] Wyjaśnienie użytych parametrów.
- [ ] Dodanie wykresu działania filtru.

### 13.08 — Czwartek
- [ ] Opis implementacji MPC.
- [ ] Opis funkcji celu.
- [ ] Opis ograniczeń.
- [ ] Opis generowania decyzji.

### 14.08 — Piątek
- [ ] Opis interfejsu użytkownika.
- [ ] Dodanie screenów aplikacji.
- [ ] Opis sposobu interpretacji decyzji przez użytkownika.

### 15.08 — Sobota
- [ ] Poprawki rozdziału implementacyjnego.
- [ ] Uzupełnienie rysunków i tabel.
- [ ] Sprawdzenie, czy opis zgadza się z kodem.

**Efekt tygodnia:** napisany rozdział projektowo-implementacyjny.

---

## Tydzień 8: Testy i wyniki  
### 16 sierpnia – 22 sierpnia

**Cel tygodnia:** opisać badania, wyniki oraz ocenę działania aplikacji.

### 16.08 — Niedziela
- [ ] Opis metodologii testów.
- [ ] Opis danych testowych.
- [ ] Opis wybranych instrumentów finansowych.

### 17.08 — Poniedziałek
- [ ] Opis parametrów testów.
- [ ] Opis horyzontu predykcji.
- [ ] Opis ograniczeń przyjętych w testach.

### 18.08 — Wtorek
- [ ] Przygotowanie i opis tabel z wynikami.
- [ ] Stopa zwrotu.
- [ ] Liczba transakcji.
- [ ] Porównanie z benchmarkiem.

### 19.08 — Środa
- [ ] Dodanie wykresów wynikowych.
- [ ] Wykres ceny i estymacji.
- [ ] Wykres decyzji inwestycyjnych.
- [ ] Wykres porównawczy strategii.

### 20.08 — Czwartek
- [ ] Analiza wyników.
- [ ] Omówienie, kiedy metoda działa dobrze.
- [ ] Omówienie, kiedy metoda działa słabiej.

### 21.08 — Piątek
- [ ] Opis ograniczeń aplikacji.
- [ ] Opis ograniczeń danych.
- [ ] Opis ograniczeń modelu.

### 22.08 — Sobota
- [ ] Wnioski z badań.
- [ ] Poprawki całego rozdziału wynikowego.
- [ ] Sprawdzenie spójności tabel i wykresów.

**Efekt tygodnia:** napisany rozdział badawczy.

---

## Tydzień 9: Zakończenie i redakcja  
### 23 sierpnia – 31 sierpnia

**Cel tygodnia:** ukończyć pracę, poprawić styl i przygotować wersję końcową.

### 23.08 — Niedziela
- [ ] Pisanie zakończenia.
- [ ] Podsumowanie celu pracy.
- [ ] Podsumowanie wykonanej aplikacji.

### 24.08 — Poniedziałek
- [ ] Opis możliwości dalszego rozwoju.
- [ ] Możliwe ulepszenia modelu.
- [ ] Możliwe ulepszenia interfejsu.
- [ ] Możliwe dodanie innych danych wejściowych.

### 25.08 — Wtorek
- [ ] Uporządkowanie bibliografii.
- [ ] Sprawdzenie cytowań.
- [ ] Sprawdzenie źródeł przy teorii i danych.

### 26.08 — Środa
- [ ] Formatowanie pracy zgodnie z wymaganiami uczelni.
- [ ] Marginesy.
- [ ] Czcionka.
- [ ] Interlinia.
- [ ] Numeracja stron.

### 27.08 — Czwartek
- [ ] Sprawdzenie numeracji rysunków.
- [ ] Sprawdzenie numeracji tabel.
- [ ] Sprawdzenie numeracji wzorów.
- [ ] Sprawdzenie podpisów pod rysunkami.

### 28.08 — Piątek
- [ ] Pierwsza pełna korekta językowa.
- [ ] Usunięcie powtórzeń.
- [ ] Poprawa stylu naukowego.

### 29.08 — Sobota
- [ ] Druga korekta pracy.
- [ ] Sprawdzenie logicznego przejścia między rozdziałami.
- [ ] Sprawdzenie, czy cel pracy został spełniony.

### 30.08 — Niedziela
- [ ] Finalne poprawki techniczne.
- [ ] Eksport do PDF.
- [ ] Sprawdzenie PDF po eksporcie.

### 31.08 — Poniedziałek
- [ ] Przygotowanie wersji do wysłania promotorowi.
- [ ] Sprawdzenie nazw plików.
- [ ] Backup pracy, kodu i załączników.
- [ ] Wysłanie pracy lub przygotowanie do oddania.

**Efekt tygodnia:** gotowa finalna wersja pracy.

---

# 1 września — finalna kontrola

### 01.09 — Wtorek
- [ ] Sprawdzenie finalnej wersji PDF.
- [ ] Sprawdzenie, czy wszystkie rysunki i tabele są widoczne.
- [ ] Sprawdzenie bibliografii.
- [ ] Sprawdzenie repozytorium z kodem.
- [ ] Sprawdzenie załączników.
- [ ] Przygotowanie krótkiego opisu projektu na obronę.
- [ ] Drobne poprawki po promotorze, jeśli będą potrzebne.

---

# Minimalny rytm pracy dziennej

## Lipiec — kod i wyniki

Każdego dnia najlepiej zrobić:

1. **2–3 godziny pracy technicznej**  
   Kodowanie najważniejszej funkcji danego dnia.

2. **1–2 godziny testów i poprawek**  
   Sprawdzenie, czy działa to, co zostało napisane.

3. **30 minut dokumentacji**  
   Krótka notatka: co działa, co nie działa, jakie są parametry, jakie są wyniki.

## Sierpień — pisanie pracy

Każdego dnia najlepiej zrobić:

1. **2–3 godziny pisania głównego tekstu**  
   Jeden konkretny fragment rozdziału.

2. **1 godzina uzupełniania rysunków, tabel i bibliografii**

3. **30 minut korekty wcześniejszego tekstu**

---

# Zasady kontroli projektu

- [ ] Po 1 sierpnia nie dodawać dużych nowych funkcji.
- [ ] Każdego dnia robić backup kodu lub pracy.
- [ ] Co tydzień eksportować aktualną wersję pracy do PDF.
- [ ] Wszystkie wykresy zapisywać w dobrej jakości.
- [ ] Każdy wynik testów zapisywać od razu do tabeli.
- [ ] Nie zostawiać bibliografii na ostatni dzień.
- [ ] Nie zostawiać formatowania na ostatni dzień.
- [ ] Nie poprawiać bez końca aplikacji kosztem pisania pracy.

---

# Proponowana struktura pracy

1. **Wstęp**
   - cel pracy,
   - motywacja,
   - zakres pracy,
   - opis problemu.

2. **Podstawy teoretyczne**
   - dane giełdowe,
   - szeregi czasowe,
   - filtr Kalmana,
   - sterowanie predykcyjne MPC.

3. **Projekt aplikacji**
   - wymagania,
   - architektura,
   - przepływ danych,
   - opis modułów.

4. **Implementacja**
   - pobieranie danych z API,
   - przetwarzanie danych,
   - filtr Kalmana,
   - MPC,
   - interfejs użytkownika.

5. **Badania i wyniki**
   - metodologia testów,
   - dane testowe,
   - wyniki,
   - porównanie z benchmarkiem,
   - analiza skuteczności.

6. **Podsumowanie**
   - wnioski,
   - ograniczenia,
   - możliwości dalszego rozwoju.

---

# Status projektu

- [ ] Moduł API
- [ ] Przygotowanie danych
- [ ] Filtr Kalmana
- [ ] MPC
- [ ] Moduł decyzji
- [ ] Interfejs użytkownika
- [ ] Wykresy
- [ ] Testy historyczne
- [ ] README
- [ ] Wstęp pracy
- [ ] Teoria
- [ ] Projekt aplikacji
- [ ] Implementacja
- [ ] Wyniki
- [ ] Zakończenie
- [ ] Bibliografia
- [ ] Korekta
- [ ] Finalny PDF