#!/usr/bin/env python3
"""
🌸 Oploverz Anime Scraper 🌸
============================

A beautiful and comprehensive anime scraper for Oploverz website
that extracts anime data and pushes it to the FastAPI backend.

✨ Features:
- Beautiful console output with colors and progress bars
- Robust error handling and logging
- Professional class-based architecture
- Real-time progress tracking

Author: AnimexBE Team
Version: 2.1 - Pretty Edition
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Rich imports for beautiful console output
try:
    from rich.console import Console
    from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout
    from rich import box
    from rich.live import Live
    from rich.spinner import Spinner
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  For the best experience, install rich: pip install rich")


# Beautiful ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🌸  ╔═╗╔═╗╦  ╦╔═╗╔═╗╦═╗╔═╗╔═╗╦═╗  ╔═╗╔═╗╦═╗╔═╗╔═╗╔═╗╦═╗  🌸     ║
║         ║ ║║ ║╚╗╔╝║ ║║ ║╠╦╝╠═╣╠═╝╠╦╝  ╚═╗║  ╠╦╝╠═╣╠═╝║╣ ╠╦╝         ║
║         ╚═╝╚═╝ ╚╝ ╚═╝╚═╝╩╚═╩ ╩╩  ╩╚═  ╚═╝╚═╝╩╚═╩ ╩╩  ╚═╝╩╚═         ║
║                                                              ║
║                     ✨ Pretty Edition v2.1 ✨                ║
╚══════════════════════════════════════════════════════════════╝
"""

# Initialize Rich Console
console = Console() if RICH_AVAILABLE else None


# Configuration
class Config:
    """🎯 Configuration settings for the scraper."""
    
    # API Configuration
    API_BASE_URL = "http://127.0.0.1:8000"
    API_KEY = "gsHBrgrKQ_BQIJF_GGFjBlP73oS9-Vr6Lkr_p2ZA3g8"
    
    # Scraping Configuration
    CRAWLER_NAME = "oploverz"
    ENGINE_STATUS = "Started"
    POSTED_BY = "Admin Otakustream"
    
    # Request Configuration
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Output Configuration
    OUTPUT_FILE = Path("oploverz_data.json")
    LOG_FILE = Path("scraper.log")
    
    # Visual Configuration
    COLORS = {
        'success': 'green',
        'error': 'red',
        'warning': 'yellow',
        'info': 'cyan',
        'highlight': 'magenta',
        'dim': 'dim white'
    }
    
    # Discord Configuration
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1366464256387711087/qWU7EeGYzxYiUXXJVg4zXJ5E0tVy-RbSHZe_IKy1liXCGUVw4fq7iapyXWB5VjAQBwaQ"


def print_beautiful(message: str, style: str = "info", emoji: str = "") -> None:
    """Print beautiful colored messages."""
    if RICH_AVAILABLE and console:
        color = Config.COLORS.get(style, 'white')
        console.print(f"{emoji} {message}", style=color)
    else:
        print(f"{emoji} {message}")


def show_banner() -> None:
    """Display the beautiful ASCII banner."""
    if RICH_AVAILABLE and console:
        console.print(Panel(
            Align.center(Text(BANNER, style="cyan bold")),
            box=box.DOUBLE,
            style="magenta"
        ))
        console.print()
    else:
        print(BANNER)


def create_summary_table(stats: Dict[str, Any]) -> None:
    """Create a beautiful summary table."""
    if not RICH_AVAILABLE or not console:
        print("\n📊 CRAWLING SUMMARY:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        return
    
    table = Table(
        title="📊 Crawling Summary",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green bold")
    table.add_column("Status", justify="center")
    
    for metric, value in stats.items():
        if "Success Rate" in metric:
            rate = float(str(value).replace('%', ''))
            status = "🎉" if rate >= 90 else "⚠️" if rate >= 70 else "❌"
        elif "Successful" in metric:
            status = "✅" if int(value) > 0 else "❌"
        else:
            status = "📈"
        
        table.add_row(metric, str(value), status)
    
    console.print("\n")
    console.print(table)


# Logging Setup
def setup_logging() -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout) if not RICH_AVAILABLE else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class DiscordNotifier:
    """📢 Discord notification handler."""
    
    def __init__(self, webhook_url: str = Config.DISCORD_WEBHOOK_URL):
        self.webhook_url = webhook_url
        self.session = requests.Session()
    
    def send_message(self, message: str) -> bool:
        """Send message to Discord webhook."""
        try:
            data = {"content": message}
            response = self.session.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 204
        except Exception as e:
            print_beautiful(f"Discord notification failed: {e}", "warning", "⚠️")
            return False


class OploverzAPI:
    """🌐 API client for communicating with the FastAPI backend."""
    
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.api_key = Config.API_KEY
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
    
    def register_crawler(self) -> bool:
        """🤖 Register this crawler with the backend."""
        try:
            print_beautiful("Getting public IP address...", "info", "🌐")
            
            # Get public IP
            ip_response = self.session.get("https://api.ipify.org?format=json", timeout=10)
            ip_response.raise_for_status()
            public_ip = ip_response.json()['ip']
            
            print_beautiful(f"Public IP detected: {public_ip}", "success", "📍")
            
            # Register crawler
            crawler_data = {
                "ip": public_ip,
                "status_engine": Config.CRAWLER_NAME,
                "status_crawlers": Config.ENGINE_STATUS,
                "last_crawling": int(datetime.now().timestamp())
            }
            
            print_beautiful("Registering crawler with backend...", "info", "🔗")
            
            url = f"{self.base_url}/admin/add-crawler"
            response = self.session.post(
                url,
                params={"api_key": self.api_key},
                json=crawler_data,
                timeout=30
            )
            response.raise_for_status()
            
            print_beautiful("Crawler registered successfully!", "success", "✅")
            return True
            
        except requests.RequestException as e:
            print_beautiful(f"Failed to register crawler: {e}", "error", "❌")
            return False
    
    def get_target_url(self) -> Optional[str]:
        """🎯 Get the target URL for scraping from the backend."""
        try:
            print_beautiful("Fetching target URL from backend...", "info", "🔍")
            
            url = f"{self.base_url}/admin/get-url-for-crawler"
            params = {
                "apikey": self.api_key,
                "crawler_name": Config.CRAWLER_NAME
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            target_url = response.json()
            print_beautiful(f"Target URL retrieved: {target_url}", "success", "🎯")
            return target_url
            
        except requests.RequestException as e:
            print_beautiful(f"Failed to get target URL: {e}", "warning", "⚠️")
            return None
        except (ValueError, KeyError) as e:
            print_beautiful(f"Invalid response format: {e}", "error", "❌")
            return None
    
    def submit_anime_data(self, anime_data: Dict[str, Any]) -> bool:
        """📤 Submit anime data to the backend."""
        try:
            url = f"{self.base_url}/admin/add-anime"
            params = {"api_key": self.api_key}
            
            response = self.session.post(
                url,
                params=params,
                json=anime_data,
                timeout=30
            )
            response.raise_for_status()
            
            return True
            
        except requests.RequestException as e:
            print_beautiful(f"Failed to submit: {anime_data.get('title', 'Unknown')}", "error", "❌")
            return False


class OploverzScraper:
    """🕷️ Web scraper for Oploverz anime data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.HEADERS['User-Agent']
        })
    
    def get_anime_list(self, base_url: str = 'https://oploverz.now/anime/list-mode/') -> List[str]:
        """📋 Extract all anime URLs from the anime list page."""
        try:
            print_beautiful(f"Fetching anime list from: {base_url}", "info", "📋")
            
            response = self.session.get(base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            anime_links = set()
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']

                if href.startswith('https://www.oploverz.now/anime/') and href != base_url:
                    
                    anime_links.add(href)
            
            anime_list = list(anime_links)
            print_beautiful(f"Found {len(anime_list)} anime entries", "success", "🎬")
            return anime_list
            
        except requests.RequestException as e:
            print_beautiful(f"Failed to fetch anime list: {e}", "error", "❌")
            return []
        except Exception as e:
            print_beautiful(f"Unexpected error: {e}", "error", "💥")
            return []
    
    def scrape_episode_details(self, episode_url: str) -> Optional[str]:
        """🎬 Extract video URL from episode page."""
        try:
            response = self.session.get(episode_url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            iframe = soup.find('iframe')
            
            if iframe and iframe.has_attr('src'):
                return iframe['src']
            
            return None
            
        except requests.RequestException:
            return None
        except Exception:
            return None
    
    def parse_anime_info(self, info_section) -> Dict[str, Any]:
        """📝 Parse anime information from the info section."""
        info_data = {
            'title': None,
            'status': None,
            'studio': None,
            'released_on': None,
            'season': None,
            'type': None,
            'genres': []
        }
        
        if not info_section:
            return info_data
        
        # Extract title
        title_tag = info_section.find('h1')
        if title_tag:
            info_data['title'] = title_tag.text.strip()
        
        # Extract genres
        genres = info_section.find_all('div', class_="genxed")
        for genre_div in genres:
            genre_links = genre_div.find_all('a')
            for link in genre_links:
                info_data['genres'].append(link.text.strip())
        
        # Extract other details from detail box
        detail_box = info_section.find('div', class_='spe')
        if detail_box:
            spans = detail_box.find_all('span')
            for span in spans:
                if ':' in span.text:
                    key, value = span.text.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # Map keys to data fields
                    if 'status' in key:
                        info_data['status'] = value
                    elif 'studio' in key:
                        info_data['studio'] = value
                    elif 'released' in key:
                        info_data['released_on'] = value
                    elif 'season' in key:
                        info_data['season'] = value
                    elif 'type' in key:
                        info_data['type'] = value
        
        return info_data
    
    def extract_episodes(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """🎞️ Extract episode information from anime page."""
        episodes = []
        eps_section = soup.find('div', class_='eplister')
        
        if not eps_section:
            return episodes
        
        episode_items = eps_section.find_all('li')
        
        for ep in episode_items:
            a_tag = ep.find('a')
            ep_num = ep.find('div', class_='epl-num')
            ep_title = ep.find('div', class_='epl-title')
            ep_date = ep.find('div', class_='epl-date')
            
            if not all([a_tag, ep_num, ep_title]):
                continue
            
            ep_link = a_tag.get('href')
            episode_data = {
                'number': ep_num.text.strip(),
                'title': ep_title.text.strip(),
                'date': ep_date.text.strip() if ep_date else None,
                'url': ep_link,
                'video_url': None
            }
            
            # Get video URL if episode link exists
            if ep_link:
                video_url = self.scrape_episode_details(ep_link)
                episode_data['video_url'] = video_url
            
            episodes.append(episode_data)
        
        return episodes
    
    def scrape_anime_details(self, anime_url: str) -> Optional[Dict[str, Any]]:
        """🎭 Extract comprehensive anime details from anime page."""
        try:
            response = self.session.get(anime_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info
            info_section = soup.find('div', class_='infox')
            anime_info = self.parse_anime_info(info_section)
            
            # Extract banner image
            banner_img = soup.find('img', class_='ts-post-image wp-post-image attachment-medium_large size-medium_large')
            banner_url = banner_img.get('src') if banner_img else None
            
            # Extract synopsis
            sinopsis_div = soup.find('div', class_="entry-content")
            sinopsis = None
            if sinopsis_div:
                p_tag = sinopsis_div.find('p')
                sinopsis = p_tag.text.strip() if p_tag else None
            
            # Extract episodes
            episodes = self.extract_episodes(soup)
            
            # Parse release date
            released_on = None
            if anime_info['released_on']:
                try:
                    # Handle different date formats
                    date_formats = ["%B %d, %Y", "%d %B, %Y", "%Y-%m-%d"]
                    for fmt in date_formats:
                        try:
                            released_on = datetime.strptime(anime_info['released_on'], fmt).date()
                            break
                        except ValueError:
                            continue
                except ValueError:
                    pass
            
            # Build final anime data
            anime_data = {
                'title': anime_info['title'],
                'status': anime_info['status'],
                'studio': anime_info['studio'],
                'released_year': anime_info['released_on'],
                'season': anime_info['season'],
                'type': anime_info['type'],
                'posted_by': Config.POSTED_BY,
                'released_on': released_on.isoformat() if released_on else None,
                'updated_on': None,
                'banner': banner_url,
                'sinopsis': sinopsis,
                'episodes': episodes,
                'genres': anime_info['genres']
            }
            
            return anime_data
            
        except requests.RequestException:
            return None
        except Exception:
            return None


class OploverzCrawler:
    """🤖 Main crawler orchestrator with beautiful output."""
    
    def __init__(self):
        self.api_client = OploverzAPI()
        self.scraper = OploverzScraper()
        self.discord = DiscordNotifier()
        self.scraped_data: List[Dict[str, Any]] = []
        self.stats = {
            'total_processed': 0,
            'successful_submissions': 0,
            'failed_submissions': 0,
            'start_time': None,
            'end_time': None
        }
    
    def run(self) -> bool:
        """🚀 Execute the complete crawling process with beautiful progress tracking."""
        show_banner()
        
        print_beautiful("Initializing Oploverz Crawler...", "info", "🚀")
        self.stats['start_time'] = datetime.now()
        
        # Send Discord notification
        self.discord.send_message("🚀 Mulai scraping anime dari Oploverz...")
        
        # Step 1: Register crawler
        if not self.api_client.register_crawler():
            print_beautiful("Failed to register crawler. Aborting.", "error", "❌")
            return False
        
        # Step 2: Get target URL
        target_url = self.api_client.get_target_url()
        if not target_url:
            print_beautiful("Using default URL...", "warning", "⚠️")
            target_url = "https://oploverz.my/anime/list-mode/"
        
        # Step 3: Get anime list
        anime_urls = self.scraper.get_anime_list(target_url)
        if not anime_urls:
            print_beautiful("No anime URLs found. Aborting.", "error", "❌")
            return False
        
        # Step 4: Process each anime with beautiful progress
        self.process_anime_with_progress(anime_urls)
        
        # Step 5: Save results and show summary
        self.save_results()
        self.show_final_summary()
        
        return self.stats['successful_submissions'] > 0
    
    def process_anime_with_progress(self, anime_urls: List[str]) -> None:
        """⚡ Process anime with beautiful progress bars."""
        total_anime = len(anime_urls)
        self.stats['total_processed'] = total_anime
        
        print_beautiful(f"Starting to process {total_anime} anime...", "info", "⚡")
        
        if RICH_AVAILABLE and console:
            self.process_with_rich_progress(anime_urls)
        else:
            self.process_with_simple_progress(anime_urls)
    
    def process_with_rich_progress(self, anime_urls: List[str]) -> None:
        """🌈 Process with Rich progress bars."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("🎬 Scraping anime...", total=len(anime_urls))
            
            for index, anime_url in enumerate(anime_urls, 1):
                # Update progress description with current anime
                anime_name = anime_url.split('/')[-2] if anime_url.endswith('/') else anime_url.split('/')[-1]
                progress.update(task, description=f"🎬 Processing: {anime_name[:30]}...")
                
                # Scrape anime details
                anime_data = self.scraper.scrape_anime_details(anime_url)
                if not anime_data:
                    self.stats['failed_submissions'] += 1
                    progress.advance(task)
                    continue
                
                # Submit to API
                if self.api_client.submit_anime_data(anime_data):
                    self.stats['successful_submissions'] += 1
                    self.scraped_data.append(anime_data)
                    
                    # Send Discord notification every 5 successful submissions
                    if index % 5 == 0:
                        self.discord.send_message(f"✅ [{index}/{len(anime_urls)}] '{anime_data.get('title', 'Unknown')}' berhasil dikirim ke API")
                    
                    # Show success message occasionally
                    if index % 5 == 0:
                        console.print(f"✅ Successfully processed: [green]{anime_data.get('title', 'Unknown')}[/green]")
                else:
                    self.stats['failed_submissions'] += 1
                
                progress.advance(task)
                
                # Small delay to not overwhelm the server
                time.sleep(0.1)
    
    def process_with_simple_progress(self, anime_urls: List[str]) -> None:
        """📈 Process with simple progress indicators."""
        total_anime = len(anime_urls)
        
        for index, anime_url in enumerate(anime_urls, 1):
            print(f"[{index}/{total_anime}] ({index/total_anime*100:.1f}%) Processing anime...")
            
            # Scrape anime details
            anime_data = self.scraper.scrape_anime_details(anime_url)
            if not anime_data:
                self.stats['failed_submissions'] += 1
                continue
            
            # Submit to API
            if self.api_client.submit_anime_data(anime_data):
                self.stats['successful_submissions'] += 1
                self.scraped_data.append(anime_data)
                
                # Send Discord notification every 5 successful submissions
                if index % 5 == 0:
                    self.discord.send_message(f"✅ [{index}/{total_anime}] '{anime_data.get('title', 'Unknown')}' berhasil dikirim ke API")
                
                print(f"✅ Success: {anime_data.get('title', 'Unknown')}")
            else:
                self.stats['failed_submissions'] += 1
    
    def save_results(self) -> None:
        """💾 Save scraped data to local JSON file."""
        try:
            with open(Config.OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, ensure_ascii=False, indent=2, default=str)
            
            print_beautiful(f"Results saved to: {Config.OUTPUT_FILE}", "success", "💾")
            
        except Exception as e:
            print_beautiful(f"Failed to save results: {e}", "error", "❌")
    
    def show_final_summary(self) -> None:
        """📊 Display beautiful final summary."""
        self.stats['end_time'] = datetime.now()
        duration = self.stats['end_time'] - self.stats['start_time']
        
        success_rate = (self.stats['successful_submissions'] / self.stats['total_processed'] * 100) if self.stats['total_processed'] > 0 else 0
        
        summary_stats = {
            "Total Anime Processed": self.stats['total_processed'],
            "Successful Submissions": self.stats['successful_submissions'],
            "Failed Submissions": self.stats['failed_submissions'],
            "Success Rate": f"{success_rate:.1f}%",
            "Duration": str(duration).split('.')[0],
            "Average Speed": f"{self.stats['total_processed'] / duration.total_seconds() * 60:.1f} anime/min"
        }
        
        create_summary_table(summary_stats)
        
        # Send final Discord notification
        if success_rate >= 90:
            message = "🎉 Scraping selesai! Semua data berhasil dikirim!"
            print_beautiful("Crawling completed successfully! 🎉", "success", "🎉")
        elif success_rate >= 70:
            message = "⚠️ Scraping selesai dengan beberapa masalah"
            print_beautiful("Crawling completed with some issues ⚠️", "warning", "⚠️")
        else:
            message = "❌ Scraping selesai dengan banyak kegagalan"
            print_beautiful("Crawling completed with many failures ❌", "error", "❌")
        
        self.discord.send_message(message)


def main():
    """🎯 Main entry point with beautiful error handling."""
    try:
        crawler = OploverzCrawler()
        success = crawler.run()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_beautiful("\nCrawler interrupted by user. Goodbye! 👋", "warning", "👋")
        sys.exit(1)
    except Exception as e:
        print_beautiful(f"Unexpected error: {e}", "error", "💥")
        sys.exit(1)


if __name__ == "__main__":
    main()