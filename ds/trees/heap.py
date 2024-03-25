class maxHeap:
    def __init__(self):
        self.a = []
        self.n=0
    def insert(self,x):
        if(self.n==0):
            self.a.append(x)
            self.n+=1
            return
        self.a.append(x)
        self.n+=1
        current=n-1
        ota=(current-1)//2
        while self.a[current]>self.a[ota] and current>0:
            self.a[current],self.a[ota]=self.a[ota],self.a[current]
            current=ota
            ota=(current-1)//2
TOKEN = '6741489602:AAGTMECus2iIQ4_Q-2T9gPwdMrgZjr2chtU'