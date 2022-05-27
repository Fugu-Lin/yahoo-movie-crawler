from models.Yahoo_Movie_Crawler import MovieCrawler
from models.Firebase_Operation  import FirebaseOperation
import datetime

def updateNewMovieIntoHistoryList(fb, movie):
    name        = movie["movie_name"]
    basicInfo   = movie["movie_basic_info"]
    detailed    = movie["movie_detailed"]
    releaseInfo = detailed["release_info"]

    data = {
        "english_name" : "%s" %(basicInfo["movie_eng_name"]),
        "release_time" : "%s" %(basicInfo["movie_release_time"]),
        "anticipation" : "%s" %(basicInfo["movie_anticipation"]),
        "types"        : "%s" %(detailed["movie_type"]),
        "mins"         : "%s" %(releaseInfo["mins"]),
        "company"      : "%s" %(releaseInfo["company"]),
        "imdb_rating"  : "%s" %(releaseInfo["imdb"]),
        "director"     : "%s" %(releaseInfo["director"]),
        "cast"         : "%s" %(releaseInfo["cast"]),
        "rated"        : "%s" %(detailed["rated"]),
        "story"        : "%s" %(detailed["story"]),
    }

    fb.create(collectionName="歷史電影資訊", key=name, value=data)

def uploadMovieScheduleTime(fb, name, date, scheduleTime):
    if (scheduleTime != None):
        for region in scheduleTime:
            for data in scheduleTime[region]:
                for movieFormat in data["movie_start_times"]:
                    title = str(data['theater_name'])+"{"+movieFormat+"}"
                    value = {
                        "%s" %(title) : "%s" %(data["movie_start_times"][movieFormat])
                    }
                    fb.setSubCollection("電影時刻表", name, date, region, value)

def uploadMoviesInfo(fb, moviesInfo):
    for movie in moviesInfo:
        basicInfo   = movie["movie_basic_info"]
        if(len(basicInfo) != 0):
            updateNewMovieIntoHistoryList(fb, movie)
        date        = datetime.datetime.today().strftime("%Y-%m-%d")
        uploadMovieScheduleTime(fb, movie["movie_name"], date, movie["movie_schedule_time"])

if __name__ == '__main__':
    url            = "https://movies.yahoo.com.tw/movie_thisweek.html?page="
    area           = ["宜蘭", "新竹"]
    fb             = FirebaseOperation("web-crawler-96aae-firebase-adminsdk-cgz5n-9741f6fe75.json")
    existMovieList = fb.retrieveAllDocument("歷史電影資訊")
    movies         = MovieCrawler(url, area, existMovieList)
    moviesInfo     = movies.getAllMovie(5)

    uploadMoviesInfo(fb, moviesInfo)

    