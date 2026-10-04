import time
import re
import getpass
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.text import Text

# Initialize Rich Console
console = Console()

# Sci-Fi Cyberpunk ASCII Banner
BANNER = """
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██████╗ ██╗██╗   ██╗███████╗███╗   ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║██║   ██║██╔════╝████╗  ██║
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██████╔╝██║██║   ██║█████╗  ██╔██╗ ██║
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔═══╝ ██║██║   ██║██╔══╝  ██║╚██╗██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║     ██║╚██████╔╝███████╗██║ ╚████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝
               [ SYSTEM OPERATIONAL :: TESLA DATA INFILTRATION ]
"""


def play_completion_sound():
    """Plays a sound notification depending on the OS upon completion."""
    try:
        import platform
        os_name = platform.system()
        if os_name == "Windows":
            import winsound
            winsound.Beep(1000, 500)
            winsound.Beep(1500, 700)
        elif os_name == "Darwin":  # macOS
            import os
            os.system("afplay /System/Library/Sounds/Glass.aiff")
        else:  # Linux
            import os
            os.system("play -q -n synth 0.1 sin 880 || printf '\\a'")
    except Exception as e:
        console.print(f"[bold red][!] SOUND SIGNAL FAILED: {e}[/bold red]")


def send_email_notification(sender_email, sender_password, recipient_email, total_records):
    """Sends an email notification when scraping is completed."""
    try:
        subject = "⚡ [CYBER-BOT] DATA EXTRACTION COMPLETED"
        body = f"""[SYSTEM TRANSMISSION RECEIPT]

Target Sector: Bilbasen Denmark
Status: Extraction Successful
Payload Harvested: {total_records} Tesla Vehicle Records
Local File Saved: bilbasen_all_teslas_en.csv

End of transmission.
"""
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        console.print("[bold bright_green][✔] TRANSMISSION DISPATCHED TO TARGET EMAIL[/bold bright_green]")
    except Exception as e:
        console.print(f"[bold bright_red][✘] TRANSMISSION FAILURE: {e}[/bold bright_red]")


def print_cyber_header():
    console.clear()
    console.print(Text(BANNER, style="bold bright_green"))


def scrape_bilbasen_tesla_cyberpunk():
    print_cyber_header()

    console.print(Panel("[bold green]INITIATING CYBERNETIC DATA EXTRACTION PROTOCOL...[/bold green]",
                        title="[bold bright_cyan]SYSTEM STATUS[/bold bright_cyan]", border_style="bright_cyan"))

    # --- USER INPUTS & EMAIL CONFIGURATION ---
    email_choice = console.input(
        "\n[bold bright_yellow]⚡ ENABLE COMMS RELAY (EMAIL NOTIFICATION)? (y/n): [/bold bright_yellow]").strip().lower()

    ENABLE_EMAIL = email_choice in ['y', 'yes']
    SENDER_EMAIL = ""
    SENDER_PASSWORD = ""
    RECIPIENT_EMAIL = ""

    if ENABLE_EMAIL:
        SENDER_EMAIL = console.input("[bold bright_cyan]📧 ENTER TRANSMITTER (GMAIL): [/bold bright_cyan]").strip()
        SENDER_PASSWORD = getpass.getpass("🔑 ENTER TRANSMITTER PASSKEY (APP PASSWORD): ").strip()
        RECIPIENT_EMAIL = console.input(
            "[bold bright_cyan]📩 ENTER RECEIVER (TARGET EMAIL): [/bold bright_cyan]").strip()

    console.print("\n[bold bright_green][>>>] LAUNCHING PHANTOM BROWSER CORE...[/bold bright_green]")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.bilbasen.dk/brugt/bil/tesla?includeunapproved=True"
    driver.get(url)
    time.sleep(3)

    tesla_data = []
    current_page = 1

    while True:
        console.print(Panel(f"[bold bright_cyan]SECTOR MATRIX :: SECTOR PAGE {current_page}[/bold bright_cyan]",
                            border_style="bright_green"))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all('article', class_=re.compile('bb-listing'))
        if not listings:
            listings = soup.find_all('div', class_=re.compile('listing'))

        page_links = []
        for item in listings:
            link_elem = item.find('a', href=True)
            if link_elem:
                full_link = link_elem['href']
                if not full_link.startswith('http'):
                    full_link = "https://www.bilbasen.dk" + full_link
                page_links.append(full_link)

        if len(page_links) == 0:
            console.print("[bold bright_red][!] NO MORE SIGNALS DETECTED IN THIS SECTOR.[/bold bright_red]")
            break

        # Cyberpunk Progress Bar
        with Progress(
                SpinnerColumn("aesthetic", finished_text="[bold bright_green]✔[/bold bright_green]"),
                TextColumn("[bold bright_cyan]{task.description}"),
                BarColumn(bar_width=40, style="bright_black", complete_style="bright_green",
                          finished_style="bold bright_green"),
                TextColumn("[bold bright_yellow]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=console
        ) as progress:

            task = progress.add_task(f"INFILTRATING SECTOR PAGE {current_page}...", total=len(page_links))

            for idx, link in enumerate(page_links, 1):
                try:
                    driver.get(link)
                    time.sleep(1.2)

                    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    text_full = detail_soup.text
                    text_lower = text_full.lower()

                    # 1. Title
                    title_elem = detail_soup.find('h1') or detail_soup.find('title')
                    title = title_elem.text.strip() if title_elem else "Tesla"

                    # 2. Total Cash Price
                    raw_price = "N/A"
                    price_elems = detail_soup.find_all(class_=re.compile(r'price|bas-price|vip-price-tag'))
                    for pe in price_elems:
                        txt = pe.text.strip()
                        if "md" in txt.lower() or "måned" in txt.lower():
                            continue
                        if "kr" in txt.lower() or re.search(r'\d{3}\.\d{3}', txt):
                            raw_price = txt
                            break

                    if raw_price == "N/A":
                        price_match = re.search(r'(\d{1,3}(?:\.\d{3})+|\d{5,7})\s*kr', text_lower)
                        if price_match:
                            raw_price = price_match.group(1)

                    clean_price = re.sub(r'[^\d]', '', raw_price)
                    if not clean_price:
                        clean_price = "NOT DETECTED"

                    model_type = "Model 3" if "Model 3" in title else \
                        "Model Y" if "Model Y" in title else \
                            "Model S" if "Model S" in title else \
                                "Model X" if "Model X" in title else "Tesla (Other)"

                    # 3. Model Year
                    year_match = re.search(r'(?:modelår|modelårg|årgang)\s*[:=]?\s*(20\d{2})', text_lower)
                    if not year_match:
                        year_match = re.search(r' (20[12]\d) ', title)
                    if not year_match:
                        year_match = re.search(r' (20[12]\d) ', text_lower)
                    model_year = year_match.group(1) if year_match else "NOT SPECIFIED"

                    # 4. First Registration Date
                    reg_match = re.search(
                        r'(?:1\.\s*reg|første\s*registrering|reg\.\s*dato|registreringsdato)\s*[:=]?\s*([0-3]?\d[./\-][0-1]?\d[./\-]?20\d{2}|[0-1]?\d[./\-][20\d{2}]|20\d{2})',
                        text_lower)
                    if not reg_match:
                        reg_match = re.search(r'([0-3]?\d/[0-1]?\d-20\d{2}|[0-1]?\d/20\d{2})', text_lower)
                    reg_date = reg_match.group(1) if reg_match else "NOT SPECIFIED"

                    # 5. Drivetrain
                    if any(k in text_lower for k in
                           ["awd", "4wd", "dual motor", "4x4", "all wheel drive", "plaid", "performance"]):
                        drivetrain = "AWD (DUAL MOTOR)"
                    elif any(k in text_lower for k in ["rwd", "2wd", "rear wheel drive", "standard range"]):
                        drivetrain = "RWD (SINGLE MOTOR)"
                    else:
                        drivetrain = "RWD (SINGLE MOTOR)" if "model 3" in text_lower or "model y" in text_lower else "AWD (DUAL MOTOR)"

                    # 6. Mileage (Km)
                    km_match = re.search(r'(\d{1,3}(?:\.\d{3})+|\d+)\s*(?:km|kilometre)', text_lower)
                    km = f"{km_match.group(1)} km" if km_match else "NOT SPECIFIED"

                    # 7. WLTP Range
                    wltp_match = re.search(r'(?:wltp|rækkevidde|range)\s*[:=]?\s*(\d{3,4})\s*(?:km)?', text_lower)
                    if not wltp_match:
                        wltp_match = re.search(r'(\d{3,4})\s*km\s*(?:rækkevidde|wltp)', text_lower)
                    wltp_range = f"{wltp_match.group(1)} km" if wltp_match else "NOT SPECIFIED"

                    # 8. Battery Capacity
                    bat_cap_match = re.search(r'(\d{2,3}(?:[.,]\d)?)\s*(?:kwh|kw/h)', text_lower)
                    bat_capacity = f"{bat_cap_match.group(1)} kWh" if bat_cap_match else "NOT SPECIFIED"

                    # 9. Energy Consumption (Wh/km)
                    consumption_match = re.search(r'(\d{2,3})\s*(?:wh/km|wh/mi)', text_lower)
                    if not consumption_match:
                        kwh_100_match = re.search(r'(\d{2}(?:[.,]\d)?)\s*kwh\s*/?\s*100\s*km', text_lower)
                        if kwh_100_match:
                            try:
                                val = float(kwh_100_match.group(1).replace(',', '.')) * 10
                                consumption = f"{int(val)} Wh/km"
                            except Exception:
                                consumption = "NOT SPECIFIED"
                        else:
                            consumption = "NOT SPECIFIED"
                    else:
                        consumption = f"{consumption_match.group(1)} Wh/km"

                    # 10. Top Speed
                    top_speed_match = re.search(
                        r'(?:topfart|top speed|maksimum hastighed)\s*[:=]?\s*(\d{3})\s*(?:km/t|km/h)?', text_lower)
                    if not top_speed_match:
                        top_speed_match = re.search(r'(\d{3})\s*(?:km/t|km/h)\s*(?:topfart|maksimum)', text_lower)
                    top_speed = f"{top_speed_match.group(1)} km/h" if top_speed_match else "NOT SPECIFIED"

                    # 11. Color Mapping
                    color_map = {
                        "hvid": "WHITE", "sort": "BLACK", "grå": "GREY",
                        "sølv": "SILVER", "blå": "BLUE", "rød": "RED"
                    }
                    color = "NOT SPECIFIED"
                    color_match = re.search(r'farve\s*[:=]?\s*([a-zæøå]+)', text_lower)
                    if color_match:
                        found_color = color_match.group(1).strip()
                        for c_key, c_val in color_map.items():
                            if c_key in found_color:
                                color = c_val
                                break
                        if color == "NOT SPECIFIED":
                            color = found_color.upper()
                    else:
                        for c_key, c_val in color_map.items():
                            if f" {c_key} " in f" {text_lower} " or f"{c_key}met" in text_lower:
                                color = c_val
                                break

                    # 12. Seller Name & Phone Number
                    seller_elem = detail_soup.find('div', class_=re.compile('seller|vip-seller-info|dealer')) or \
                                  detail_soup.find('a', class_=re.compile('seller-name|dealer-name')) or \
                                  detail_soup.find('h2', class_=re.compile('seller|dealer'))
                    seller_name = seller_elem.text.strip() if seller_elem else "UNKNOWN ENTITY"

                    try:
                        phone_btn = driver.find_element(By.XPATH,
                                                        "//button[contains(text(), 'Tlf') or contains(text(), 'Telefon') or contains(@class, 'phone')]")
                        driver.execute_script("arguments[0].click();", phone_btn)
                        time.sleep(0.3)
                        detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    except Exception:
                        pass

                    phone_match = re.search(r'(\+45\s*)?(\d{2}\s*\d{2}\s*\d{2}\s*\d{2}|\d{8})', detail_soup.text)
                    seller_phone = phone_match.group(0).strip() if phone_match else "ENCRYPTED / RESTRICTED"

                    # 13. Processor & Heat Pump Features
                    desc_elem = detail_soup.find('div', class_=re.compile('description')) or detail_soup.find('body')
                    desc_text = desc_elem.text.lower() if desc_elem else ""

                    processor = "AMD RYZEN" if ("ryzen" in desc_text or "amd" in desc_text) else (
                        "INTEL ATOM" if ("atom" in desc_text or "intel" in desc_text) else "NOT SPECIFIED")
                    battery_chem = "LFP (LITHIUM IRON)" if (
                                "lfp" in desc_text or "blade" in desc_text or "jernfosfat" in desc_text) else "NMC / NCA / UNKNOWN"
                    heat_pump = "YES" if ("varmepumpe" in desc_text or "heat pump" in desc_text) else "NO / UNKNOWN"

                    record = {
                        "Model": model_type,
                        "Title": title,
                        "Model Year": model_year,
                        "First Registration Date": reg_date,
                        "Drivetrain": drivetrain,
                        "Color": color,
                        "Price (DKK Raw)": clean_price,
                        "Mileage": km,
                        "WLTP Range": wltp_range,
                        "Battery Capacity": bat_capacity,
                        "Consumption (Wh/km)": consumption,
                        "Top Speed": top_speed,
                        "Seller Name": seller_name,
                        "Seller Phone": seller_phone,
                        "Processor": processor,
                        "Battery Chem": battery_chem,
                        "Heat Pump": heat_pump,
                        "Listing URL": link
                    }

                    tesla_data.append(record)
                    progress.update(task, advance=1)

                    # Cyber-Matrix Table Display
                    table = Table(
                        title=f"⚡ HARVESTED NODE #{len(tesla_data):03d} [PAGE {current_page}]",
                        show_header=True,
                        header_style="bold bright_cyan on black",
                        border_style="bright_green"
                    )
                    table.add_column("SYSTEM PARAMETER", style="bold bright_yellow", width=20)
                    table.add_column("EXTRACTED VALUE", style="bold bright_green")

                    table.add_row("MODEL CHASSIS", record['Model'])
                    table.add_row("NODE IDENTIFIER",
                                  record['Title'][:45] + "..." if len(record['Title']) > 45 else record['Title'])
                    table.add_row("YEAR / REGISTRATION",
                                  f"{record['Model Year']} [{record['First Registration Date']}]")
                    table.add_row("VALUATION", f"{record['Price (DKK Raw)']} DKK")
                    table.add_row("DISTANCE METRIC", record['Mileage'])
                    table.add_row("DRIVE MATRIX", record['Drivetrain'])
                    table.add_row("HARDWARE ARCH", f"CPU: {record['Processor']} | HEAT PUMP: {record['Heat Pump']}")

                    console.print(table)

                except Exception as e:
                    console.print(f"[bold bright_red][!] ANOMALY IN NODE ({link}): {e}[/bold bright_red]")
                    progress.update(task, advance=1)
                    continue

        current_page += 1
        next_url = f"https://www.bilbasen.dk/brugt/bil/tesla?includeunapproved=True&page={current_page}"
        driver.get(next_url)
        time.sleep(2)

    driver.quit()

    # Save to CSV
    df = pd.DataFrame(tesla_data)
    df.to_csv("bilbasen_all_teslas_en.csv", index=False, encoding='utf-8-sig')

    # Cyberpunk Completion Screen
    console.print(Panel.fit(
        f"[bold bright_green]⚡ MISSION ACCOMPLISHED :: INFILTRATION COMPLETE[/bold bright_green]\n"
        f"[bold bright_cyan]TOTAL HARVESTED NODES:[/bold bright_cyan] [bold bright_yellow]{len(df)}[/bold bright_yellow]\n"
        f"[bold bright_cyan]DATASTORE FILE saved:[/bold bright_cyan] [bold bright_green]bilbasen_all_teslas_en.csv[/bold bright_green]",
        title="[bold bright_green]SYSTEM NOTICE[/bold bright_green]",
        border_style="bright_green"
    ))

    # Play Completion Sound
    play_completion_sound()

    # Send Email Notification
    if ENABLE_EMAIL:
        send_email_notification(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, len(df))


if __name__ == "__main__":
    scrape_bilbasen_tesla_cyberpunk()