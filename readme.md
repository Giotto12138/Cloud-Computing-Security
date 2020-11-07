# website address: 
https://qingshan-cloud-security.ue.r.appspot.com/


## lab1     Write an “AppEngine Standard” App
1. A simple event management website based on Flask + GCP. All HTML and JavaScript is served statically to keep secure. 
2. Users can upload events and dates, or delete events.   
3. The website could update the remaining time of the event in real time and delete expired events.  
4. Yearless dates work, showing time to next occurrence of a matching date (e.g., 03-01 means “every March 1st”)  


## lab2     Password-Based Authentication
1. Added authentication to the website. All of the events are tied to one and only one user; every user manages a unique set of data just for them. When not logged in, the user is automatically directed to a login page.  
2. All interactions are over HTTPS to secure data transmitting.  
3. Provided a registration page that allows the user to provide a username and password, then immediately logs them in and redirects them to the main page.  
4. Provided a login page that allows the user to provide a username and password. If the username and password are valid, let the user log in.  
5. Users must login with an opaque session token. Implemented this function without built-in functions like flask.session or flask.login. Users could register, login, and logout with a session token. Session tokens expire after 1 hour. Enforce this by deleting the cookie when an expired session token is used.  
6. Added a logout button that invalidates the session token, removes the cookie, and redirects the user to the login page.  
7. Only secure derivatives of passwords are stored in the database. Used Bcypt library for key stretching.  
8. built a migration function, which could migrate old data to the first user (or a user that you want to have the original data).
9. Check the login status of users in real time. JSON calls will redirect the entire browser window to the login page when they fail due to a missing (or expired) session token.  



## lab3     Implement an OpenID Connect Client
1. Implemented an OpenID Connect Client to login with Google. Users could click a third-party OpenID Connect button to their login page.
2. Added CSRF protection by double cookie verification.


## Lab 4   Introduction to Docker
1. Installed docker and pulled the base image from Docker Hub.
2. Wrote HTTP server code that outputs “Hello, World!” from port 8080 (from inside).
3. Wrote Dockerfile. 
4. Wrote a little script that outputs the URL you should go to(ip address and port) in order to see the output.


## Lab 5
