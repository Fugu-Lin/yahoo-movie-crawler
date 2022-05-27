from bs4 import BeautifulSoup
import googlemaps
import requests
import datetime
import json

class MovieCrawler:
    def __init__(self, url, area, existMovieList):
        self.url            = url
        self.requestHeaders = {'User-Agent': 'Mozilla/5.0'}
        self.numberOfMovies = 0
        self.searchArea     = area
        self.gmaps          = googlemaps.Client(key='AIzaSyAuBskIN3x5-067Ex5n3ZyftqMnjmZR_ik')
        self.existMovieList = existMovieList
        self.movieData      = []

    def __getSoup(self, url):
        res  = requests.get(url, headers=self.requestHeaders)
        soup = BeautifulSoup(res.text, 'lxml')
        return soup
        
    def __getAPISoup(self, url):
        res  = requests.get(url, cookies={'over18': '1'}, headers=self.requestHeaders) 
        view = json.loads(res.text)['view']
        soup = BeautifulSoup(view, "html.parser")
        return soup

    def __getMovieId(self, url):
        if (url != None):
            id = url.split("/id=")[1]
            return id

    def __getMovieName(self, releaseInfo):
        return releaseInfo.find('div', 'release_movie_name').a.text.strip()

    def __getMovieEngName(self, releaseInfo):
        return releaseInfo.find('div', 'en').a.text.strip()

    def __getMovieReleaseTime(self, releaseInfo):
        return releaseInfo.find('div', 'release_movie_time').text.split('：')[-1].strip()

    def __getMovieAnticipation(self, releaseInfo):
        return releaseInfo.find('div', 'leveltext').text.replace(" ", "").replace("\n", "").replace("網友想看", "") if releaseInfo.find('div', 'leveltext') != None else ""

    def __getMovieBasicInfo(self, releaseInfo):
        movieName         = self.__getMovieName(releaseInfo)
        movieEngName      = self.__getMovieEngName(releaseInfo)
        movieReleaseTime  = self.__getMovieReleaseTime(releaseInfo)
        movieAnticipation = self.__getMovieAnticipation(releaseInfo)
        # To Do 抓取youtube的第一筆預告
        # moviePreviewURL   = "https://www.youtube.com/results?search_query={movieName}預告"
        return {"movie_name": movieName, "movie_eng_name": movieEngName, "movie_release_time": movieReleaseTime, "movie_anticipation": movieAnticipation}

    def __getLevelName(self, movieIntroInfoR):
        levelName = ' '.join(level.a.text.strip() for level in movieIntroInfoR.find_all('div', 'level_name'))
        return levelName

    def __getReleaseInfo(self, movieIntroInfoR):

        completeReleaseInfo = {
            "mins"    : "",
            "company" : "",
            "imdb"    : "",
            "director": [],
            "cast"    : [],
        }

        spans = movieIntroInfoR.find_all('span')
        for span in spans:
            if "片　　長：" in span.text.strip():
                completeReleaseInfo["mins"]     = span.text.strip().replace("片\u3000\u3000長：", "")
            elif "發行公司：" in span.text:
                completeReleaseInfo["company"]  = span.text.strip().replace("發行公司：", "")
            elif "IMDb分數：" in span.text:
                completeReleaseInfo["imdb"]     = span.text.strip().replace("IMDb分數：", "")
        
        movieIntroLists = movieIntroInfoR.find_all("span", "movie_intro_list")
        for spanlist in movieIntroLists:
            if "導演：" in spanlist.text:
                completeReleaseInfo["director"] = spanlist.text.strip().replace("\n", "").replace(" ", "").replace("導演：", "")
            else:
                completeReleaseInfo["cast"]     = spanlist.text.strip().replace("\n", "").replace(" ", "").replace("演員：", "")
        return completeReleaseInfo

    def __getRated(self, movieIntroInfoR):
        icon = movieIntroInfoR.find('div')
        if   len(icon["class"]) == 0:
            return "未提供分級資訊"
        elif icon["class"][0] == "icon_0":
            return "普遍級"
        elif icon["class"][0] == "icon_6":
            return "保護級"
        elif icon["class"][0] == "icon_12":
            return "輔十二級"
        elif icon["class"][0] == "icon_15":
            return "輔十五級"
        elif icon["class"][0] == "icon_18":
            return "限制級"

    def __getStory(self, detailedPage):
        return detailedPage.find("span", id="story").text.strip()

    def __getMovieInfo(self, url):
        detailedPage    = self.__getSoup(url)
        movieIntroInfoR = detailedPage.find("div", "movie_intro_info_r")
        levelNames      = self.__getLevelName(movieIntroInfoR)
        releaseInfo     = self.__getReleaseInfo(movieIntroInfoR)
        rated           = self.__getRated(movieIntroInfoR)
        story           = self.__getStory(detailedPage)
        return {"movie_type": levelNames, "release_info": releaseInfo, "rated": rated, "story": story}

    def __getTheaterInMapsInfo(self, theaterName):
        searched = self.gmaps.places(
            query=theaterName,
            language='zh-TW',
            type='movie_theater'
        )
        
        theaterAdds = str(searched['results'][0]['formatted_address'])
        theaterName = str(searched['results'][0]['name'])
        return {"theater_name": theaterName, "theater_adds": theaterAdds}

    def __getEachTapRMovieStartTime(self, tapR):
        session = {}
        for tap in tapR:
            type            = tap.find("span", "tapR").text.strip()
            movieStartTimes = self.__getMovieStartTime(tap.find_next_sibling("li", "time _c").find("div", class_= 'input_picker jq_input_picker'))
            session[type]   = movieStartTimes
        return session

    def __getMovieStartTime(self, startTimeElements):
        labels       = startTimeElements.find_all("label")
        sessionTimes = " ".join(i.text for i in labels)
        return sessionTimes

    def __getScheduleTimeDetailed(self, scheduleInfo):
        thisLocaleTheaterInfo = []
        eachTheater = scheduleInfo.find_all('ul', {'class' :'area_time _c jq_area_time'})
        for theater in eachTheater:
            theaterName       = theater.find('li', 'adds').find('a').text
            theaterPhone      = theater.find('li', 'adds').find('span').text
            theaterInMapsInfo = self.__getTheaterInMapsInfo(theaterName)
            theaterName       = theaterInMapsInfo["theater_name"]
            theaterAdds       = theaterInMapsInfo["theater_adds"]
            tapR              = theater.find_all('li', 'taps')
            movieStartTimes   = self.__getEachTapRMovieStartTime(tapR)
            th = {"theater_name": theaterName, "theater_phone": theaterPhone, "theater_adds": theaterAdds, "movie_start_times": movieStartTimes}
            thisLocaleTheaterInfo.append(th)
        return thisLocaleTheaterInfo

    def __getScheduledTime(self, id, date):
        if(id != None):
            areaTheaters = {}
            url = f"https://movies.yahoo.com.tw/ajax/pc/get_schedule_by_movie?movie_id={id}&date={date}"
            schedulePage = self.__getAPISoup(url)
            eachArea     = schedulePage.find_all('div', class_='area_timebox')
            for scheduleInfo in eachArea:
                areaName = scheduleInfo.find("div", class_="area_title").text.strip()
                if areaName in self.searchArea:
                    thisLocaleTheaterInfo  = self.__getScheduleTimeDetailed(scheduleInfo)
                    areaTheaters[areaName] = thisLocaleTheaterInfo
            return areaTheaters

    def __getMovieDetail(self, detailedLinks):
        return self.__getMovieInfo(detailedLinks)

    def getAllMovie(self, page):
        moviesInfo = []
        for i in range(1, page):
            soup         = self.__getSoup(self.url+str(i))
            releaseInfos = soup.find_all('div', 'release_info')
            for releaseInfo in releaseInfos:
                self.numberOfMovies += 1
                movieName      = self.__getMovieName(releaseInfo)
                movieBasicInfo = []
                movieDetailed  = []
                detailedLinks  = releaseInfo.find('div', 'release_btn').find_all('a')

                if self.__getMovieName(releaseInfo) not in self.existMovieList:
                    movieBasicInfo = self.__getMovieBasicInfo(releaseInfo)
                    movieDetailed  = self.__getMovieDetail(detailedLinks[0]["href"])

                id             = self.__getMovieId(detailedLinks[3].get('href'))
                date           = datetime.datetime.today().strftime("%Y-%m-%d")
                scheduleTime   = self.__getScheduledTime(id, date)

                moviesInfo.append({"movie_name": movieName, "movie_basic_info": movieBasicInfo, "movie_detailed": movieDetailed, "movie_schedule_time": scheduleTime})

        return moviesInfo

if __name__ == '__main__':
    url        = "https://movies.yahoo.com.tw/movie_intheaters.html?page="
    area       = ["宜蘭", "新竹"]
    movies     = MovieCrawler(url, area, [])
    moviesInfo = movies.getAllMovie(5)
    print(moviesInfo)
    