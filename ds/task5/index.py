import sys
from stack import *
k=sys.maxsize

def DFS(g):
  st1=Stack()
  visited=[True,False,False,False,False,False]
  i=0
  st1.push(i)
  while(not(st1.isEmpty())):
    d=st1.top()
    st1.pop()
    print(d+1, end=' ')
    for j in range(6):
      if(g[d][j]<k and visited[j]==False):
        st1.push(j)
        visited[j]=True
  print()
def minMetka(metka,visited):
  m=k
  n=0
  for i in range(len(metka)):
    if m>metka[i] and visited[i]==False:
      m=metka[i]
      n=i
  return n
def dijkstra(g, start):
    start -= 1 # Indekslash 0 dan boshlanadi, shuning uchun foydalanuvchi kiritgan boshlang'ich tugunni 1 ga kamaytiramiz.
    metka = [sys.maxsize] * 6 # Har bir tugunga eng qisqa masofani saqlash uchun ro'yxat, boshlang'ich qiymatlari cheksiz.
    metka[start] = 0 # boshlang`ich tugunga eng qisqa masofa o'z o'zidan 0 ga teng
    visited = [False] * 6
    prev = [-1] * 6  # Oldingi tugunlarni saqlaydigan ro'yxat

    for _ in range(6):
        u = minMetka(metka, visited) # Hali tashrif buyurilmagan tugunlar orasidan eng kichik `metka` qiymatiga ega tugunni topamiz.
        visited[u] = True # Topilgan tugunni tashrif buyurilgan deb belgilaymiz.
        for v in range(6): # `u` dan boshqa barcha tugunlar uchun.
            if g[u][v] < sys.maxsize and not visited[v] and metka[u] + g[u][v] < metka[v]:
                metka[v] = metka[u] + g[u][v] # Agar yangi masofa avvalgisidan kichik bo'lsa, yangilaymiz.
                prev[v] = u  # Yangilangan masofa uchun oldingi tugunni saqlab qo'yamiz.

    # Har bir nuqtaga yo'lni chiqarish
    for i in range(6):
        if i != start:
            path = []
            step = i
            while step != -1:
                path.append(step + 1)
                step = prev[step]
            path.reverse()  # Yo'lni to'g'ri ketma-ketlikda olish uchun listni teskarisiga aylantiramiz
            print(start + 1, '->', i + 1, ":", metka[i], "Path:", " -> ".join(map(str, path)))


g=[[k,7,9,k,k,14],
   [k,k,10,15,k,k],
   [k,k,k,11,k,2],
   [k,k,k,k,6,k],
   [k,k,k,k,k,9],
   [k,k,k,k,k,k]]
DFS(g)
dijkstra(g,1)