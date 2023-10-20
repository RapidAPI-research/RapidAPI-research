from github import Github
import time

ACCESS_TOKEN = ''
g = Github(ACCESS_TOKEN)
print(g.get_user().get_repos())

rate_limit = g.get_rate_limit()
rate = rate_limit.search
rate


intents = "p.rapidapi.com"

step = 1024
start = 0
end = start + step
k = 0

for i in range(0,100):
    try:
        query = intents + ' size:' + str(start) + '..' + str(end)
        result = g.search_code(query, order='desc')
        count = result.totalCount
    except:
        print("first part limit")
        time.sleep(60)
        continue
    print(start, end, count)
    if count == 1000:
        step = int(step/2)
        end = start + step
        time.sleep(2)
    else:
        with open('rapidapi.txt', 'a') as f:
            for j in result:
                try:
                    x = f.write(j.repository.html_url + '\n')
                    k = k + 1
                    print(k)
                    time.sleep(2)
                except:
                    print("second part limit")
                    time.sleep(60)
                    x = f.write(j.repository.html_url + '\n')
                    continue
        start = end
        end = start + step


