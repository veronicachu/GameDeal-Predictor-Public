# GameDeal Predictor
### Insight Data Science Fellowship Project

### Author: [Veronica Chu](https://www.linkedin.com/in/chuveronica/)

[Initial Build](http://gamedeal-predictor.xyz/)

----

### Overview:

Everyone likes a good deal - some more than others. I developed GameDeal Predictor to target gamers that enjoy deals on Steam games and want to avoid paying the full price for a game ever again. 

Using survival analysis and regression on various data surrounding a target game, GameDeal Predictor can predict what price will occur given a wait time, the probability there will be a deal tomorrow, and when the next upcoming deal will be. This allows buying gamers to make informed decisions about how to spend their money and time.

----

### Process:

I processed the 80,000+ applications (games, software, etc.) from the Steam App ID list and extracted 20,000+ games sold on the Steam store (excluding the free games) into a curated pandas dataframe. In the web application, the user inputs the target game title (e.g. Assassin's Creed Odyssey) and the amount of time they are willing to wait to purchase the game (e.g. 4 months). The algorithm pulls the price history of the target game, similar games (close starting price) by the same publisher as the target game (e.g. Ubisoft), and similar games with the same genre (e.g. action) from from IsThereAnyDeal.com. Then the algorithm consists of two parts: 1) a survival analysis on the price histories, finding the amount of time between deal occurances in the past to determine the probability the next deal will occur tomorrow and when is the next high probability (>80%) day a deal will occur, and 2) a regression analysis using the user's inputted wait time and the price histories to predict a price at the end of the wait time. 

----

### Reflection:

This was my first project in Python and using web scrapping to collect data, and I definitely learned a lot about both in working through this project. Though, because of this, I had little time to implement the secondary sources of data I had initially planned on using when charting out the project in the first week (e.g. user reviews, Steam sales events, game popularity metrics on Twitch and Youtube). This was also my first time learning about survival analysis, and it seems very well equipped for the question it answers (determining when an event will occur). It is now an analysis I can now keep in mind for use in the future!
