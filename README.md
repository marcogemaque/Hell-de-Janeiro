# Hell-de-Janeiro
A small webapp built to countabilize the shootings in Rio de Janeiro and predict how many will happen per year.

## Methodology
I used mainly dash in here, along with a whole bunch of pandas and numpy to treat the data itself, and regex to filter out and better select the tweets that were actually useful for the project. Also. the Twitter API was fundamental for this part, since it was the main source of information regarding the shootings. <br>

A huge part of this was the fact that by standard the tweets had the following format <br>
```
Local: xxx
Hora: xxx
```
That way I was able to select those who fit that description, and then proceed to remove blank spaces at the end, parenthesis, bars, and all sort of characters which made our database heterogeneous. <br>

## Deploy
Heroku will be used. Since the app is still in testing, it hasn't been deployed yet. <br>

## Ongoing Updates
Currently I'm finding a way to automatize the twitter api scraping and database update so that the app is renewed each week with new tweets.

## Shoutouts
Shoutout to @saramalvar who gave enormous help all throughout the project.
