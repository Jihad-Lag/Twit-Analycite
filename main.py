from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import print
from rich.prompt import Prompt, IntPrompt
import sys , os
from datetime import datetime, timedelta
import pandas as pd 
import tweepy
from dotenv import load_dotenv

# Uploading Keys and Tokens from file .env
file_location = './load.env'
load_dotenv(file_location)

def request_API():
 load_dotenv(file_location)
 try :
  API_KEY = os.getenv("TWITTER_API_KEY")
  API_SECRET = os.getenv("TWITTER_API_SECRET")
  ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
  ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
  if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        raise ValueError("Une ou plusieurs clés d'API sont manquantes dans le fichier .env")
 
  auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
  api=tweepy.API(auth, wait_on_rate_limit=True)
  api.verify_credentials()
  print("[green]Successfully authenticated to Twitter API[/green]")
  return api
 except Exception as e:
        print(f"[red]Authentication Error: {e}[/red]")
        sys.exit(1)
    


def Checking_the_connection():
 # To recover Keys API
 API_KEY = os.getenv("TWITTER_API_KEY")
 API_SECRET = os.getenv("TWITTER_API_SECRET")
 ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
 ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

 # Authentication with Tweepy
 auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
 auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
 api = tweepy.API(auth)

 # Checking the connection
 try:
  api.verify_credentials()
  print("[green bold]Successfully connected to Twitter API!")
 except tweepy.TweepError as e:
  print(f"[red bold]Connection error : {e}")




api = request_API()  

def search_tweets(api, search_criteria):
    try:
        query = []
        
        if search_criteria.get('keywords'):
            query.append(search_criteria['keywords'])
    
        if search_criteria.get('language'):
            query.append(f"lang:{search_criteria['language']}")
        
        if search_criteria.get('exclude_retweets', False):
            query.append("-filter:retweets")
        
        final_query = " ".join(query)
        
        start_date = search_criteria.get('start_date')
        end_date = search_criteria.get('end_date', datetime.now())
        
        tweet_count = search_criteria.get('tweet_count', 50)
        
        tweets = tweepy.Cursor(
            api.search_tweets, 
            q=final_query,
            lang=search_criteria.get('language'),
            tweet_mode='extended'
        ).items(tweet_count)
        
        tweet_data = []
        for tweet in tweets:
            tweet_data.append({
                'Text': tweet.full_text,
                'Author': tweet.user.screen_name,
                'Date': tweet.created_at,
                'Likes': tweet.favorite_count,
                'Retweets': tweet.retweet_count,
                'Language': tweet.lang
            })
        
        df = pd.DataFrame(tweet_data)
        return df
    
    except Exception as e:
        print(f"[red]Error searching tweets: {e}[/red]")
        return pd.DataFrame()

def main_keyword():
    try:
        # Get user input
        keyword = input("Enter your keyword: ")
        lang = input("Enter the language you are looking for: ")
        
        search_criteria = {
            'keywords': keyword,  # Keywords to search
            'language': lang,  # Tweet language
            'tweet_count': 50,  # Number of tweets to retrieve
            'exclude_retweets': True,  # Exclude retweets
            'start_date': datetime.now() - timedelta(days=7)  # Tweets from last 7 days
        }
        
        # Search tweets
        results = search_tweets(api, search_criteria)
        
        # Display and save results
        if not results.empty:
            print("\n[blue]Search Results:[/blue]")
            print(results)
            
            # Save to CSV
            filename = f"tweet_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results.to_csv(filename, index=False)
            print(f"[green]Results saved to {filename}[/green]")
        else:
            print("[yellow]-----------------------------[/yellow]")
    
    except Exception as e:
        print(f"[red]An error occurred: {e}[/red]")

def fetch_user_tweets(api, username, count=10):
    
    try:
        # Fetch tweets using the provided API client
        tweets = api.user_timeline(
            screen_name=username, 
            count=count, 
            tweet_mode="extended"
        )
        
        # Prepare tweet data
        tweet_data = [{
            'Username': tweet.user.name,
            'Tweet': tweet.full_text,
            'Date': tweet.created_at,
            'Retweets': tweet.retweet_count,
            'Likes': tweet.favorite_count
        } for tweet in tweets]
        
        # Create DataFrame
        df = pd.DataFrame(tweet_data)
        return df
    
    except Exception as e:
        # Detailed error handling
        print(f"[red]Error fetching tweets: {e}[/red]")
        print("[yellow]Possible reasons:[/yellow]")
        print("- Invalid username")
        print("- API connection issue")
        print("- Insufficient API permissions")
        return pd.DataFrame()

def main_User():
    # Call request_API() to get the API client
    api = request_API()

    try:
        # Get user input
        username = input("Enter the user you want to analyze: ")
        count = int(input("Enter the number of tweets you want to recover: "))
        
        # Validate input
        if count <= 0:
            print("[red]Please enter a positive number of tweets.[/red]")
            return
        
        # Fetch tweets
        df = fetch_user_tweets(api, username, count)
        
        if not df.empty:
            # Display tweets
            print(df)
            
            # Save to CSV
            csv_filename = f"{username}_tweets.csv"
            df.to_csv(csv_filename, index=False)
            print(f"[blue]Data saved to {csv_filename}[/blue]")
        else:
            print(f"[yellow]-----------------------[/yellow]")
    
    except ValueError:
        print("[red]Please enter a valid number for the count.[/red]")
    except KeyboardInterrupt:
        print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")

def display_logo():
   
    console = Console()
    logo_text = Text("""
 ████████╗██╗    ██╗██╗████████╗    █████╗ ███╗   ██╗ █████╗ ██╗     ██╗████████╗██╗ ██████╗███████╗
 ╚══██╔══╝██║    ██║██║╚══██╔══╝   ██╔══██╗████╗  ██║██╔══██╗██║     ██║╚══██╔══╝██║██╔════╝██╔════╝
    ██║   ██║ █╗ ██║██║   ██║█████╗███████║██╔██╗ ██║███████║██║     ██║   ██║   ██║██║     █████╗  
    ██║   ██║███╗██║██║   ██║╚════╝██╔══██║██║╚██╗██║██╔══██║██║     ██║   ██║   ██║██║     ██╔══╝  
    ██║   ╚███╔███╔╝██║   ██║      ██║  ██║██║ ╚████║██║  ██║███████╗██║   ██║   ██║╚██████╗███████╗
    ╚═╝    ╚══╝╚══╝ ╚═╝   ╚═╝      ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝   ╚═╝ ╚═════╝╚══════╝
""", style="bold cyan")
    console.print(logo_text)

def display_menu():
    
    console = Console()
    menu_panel = Panel(
        "[yellow]1.[/yellow] [blue]Check Connection with Twitter API[/blue]\n"
        "[yellow]2.[/yellow] [blue]Search by Keyword[/blue]\n"
        "[yellow]3.[/yellow] [blue]Search by User[/blue]\n"
        "[yellow]0.[/yellow] [red]Exit[/red]",
        title="[bold green]Twitter Analysis Tool[/bold green]",
        border_style="cyan"
    )
    console.print(menu_panel)

def main():
    
    console = Console()
    
    while True:
        
        console.clear()
        display_logo()
        display_menu()
        
        try:
            
            choice = IntPrompt.ask(
                "[bold]Enter your choice[/bold]", 
                choices=['0', '1', '2', '3'], 
                default='0'
            )
            
            
            if choice == 0:
                print("[red]Exiting the application...[/red]")
                sys.exit(0)
            
            elif choice == 1:
                
                console.rule("[bold blue]API Connection Check[/bold blue]")
                Checking_the_connection()
                Prompt.ask("[green]Press Enter to continue...[/green]")
            
            elif choice == 2:
                
                console.rule("[bold blue]Keyword Search[/bold blue]")
                main_keyword()
                Prompt.ask("[green]Press Enter to continue...[/green]")
            
            elif choice == 3:
                
                console.rule("[bold blue]User Search[/bold blue]")
                main_User()
                Prompt.ask("[green]Press Enter to continue...[/green]")
        
        except KeyboardInterrupt:
            print("\n[yellow]Operation cancelled by user.[/yellow]")
            sys.exit(0)
        
        except Exception as e:
            print(f"[red]An unexpected error occurred: {e}[/red]")
            Prompt.ask("[yellow]Press Enter to continue...[/yellow]")

if __name__ == "__main__":
    main()
