def dijkstra(g,i):
  i-=1
  metka=[k,k,k,k,k,k]
  metka[i]=0
  visited=[False,False,False,False,False,False]
  visited[i]=True
  for j in range(6):
    q=minMetka(metka,visited)
    print(q+1)
    for c in range(6):
      if g[q][c]<k and visited[c]==False and metka[q]+g[q][c]<metka[c]:
        metka[c]=metka[q]+g[q][c]
    visited[q]=True
  for j in range(len(metka)):
    print(i+1,'->',j+1,":",metka[j])

def dijkstra(g, start):
    start -= 1
    metka = [sys.maxsize] * 6
    metka[start] = 0
    visited = [False] * 6
    prev = [-1] * 6  # Oldingi tugunlarni saqlaydigan ro'yxat

    for _ in range(6):
        u = minMetka(metka, visited)
        visited[u] = True
        for v in range(6):
            if g[u][v] < sys.maxsize and not visited[v] and metka[u] + g[u][v] < metka[v]:
                metka[v] = metka[u] + g[u][v]
                prev[v] = u  # Har bir tugunga eng qisqa yo'l bilan kelgan oldingi tugunni yozib olamiz

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