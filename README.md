# beds-uni-hackathon-4-notes
[Task](https://raw.githubusercontent.com/gclikkec/beds-uni-hackathon-4/master/scenarios/are-you-taking-notes.md)

## Description
Considering the broad variety of gadgets students have and the fact that
the operating systems may range from one to another I decided that the most fitting scenario to make everybody 
happy would be to create a web app out of the task.

My intentions for this project are:
 - To make it as secure as possible so nobody could toy around with your precious notes
 - User-friendly with an intuitive interface to facilitate the new users to join the platform

I have chosen to use a `client-server architecture` because it 
makes the whole app easier to scale and maintain.


![alt text](https://raw.githubusercontent.com/Terkea/beds-uni-hackathon-4-notes/master/source_files/1.png)

![alt text](https://raw.githubusercontent.com/Terkea/beds-uni-hackathon-4-notes/master/source_files/2.png)

### Server Side
- The encryption for passwords is done by `werkzeug.security` module 
and the algorithm used is `sha256`

- Usually during the development process, even if I know it is not ideal I
 like to tweak the database schema. To keep track of all those changes I used
  `flask-migrate`
  
- Token authentication using `JSON Web Token (JWT)`

### Client Side
For the web interface I been using:

- `AdminLTE` which is a responsive bootstrap prebuild theme
- `Summernote` as the text editor for creating notes

All the inputs are validated and sterilized before they get processed to prevent `sql injection` or `XSS`

If I had more time I would had used:
- `react.js` on the front end 
- firebase real time database from google
- lazy loading

### Requirements
To install all the requirements necessarily for this project just run

`pip install -r requirements.txt` 