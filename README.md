# shift-scraper

A Python program to retrieve, parse, and add shift data to my Google Calendar. requests retrieves the raw HTML, which is then parsed with BeautifulSoup4. Finally, the program requests Google OAuth authentiacation and, if successful, invokes the Google calendar API to add the calendar events.