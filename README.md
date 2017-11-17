# python-tp-cluster-availability
TP python pour MR.Gilles Giraud 


To launch the project you need to start 3 server on 3 different terminale.
To do this : 
- You need to be place on the repository on the project 
- In the terminal 1, use this command : 
  ./series-manager-server-ft.py 30001 1
  
  - In the terminal 2, use this command : 
  ./series-manager-server-ft.py 30002 2
  
  - In the terminal 3, use this command : 
  ./series-manager-server-ft.py 30003 3
  
  
  If you stop the terminal 2, it will write on 2 other that the server is down.
  If you stop terminal 1 (the master), server 3 become the master.
  
  
  
