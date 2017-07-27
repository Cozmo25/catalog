# Catalog Project

# INSTRUCTIONS

## How to run the project
1. Download or clone the project folder (catalog)
2. Project Python & python library dependencies are:
    * Vagrant Linux VM
    * Python 2.7
    * Flask Python Framework
    * SQL Alchemy
    * oauth2client
    * application.py
    * database_setup.py
    * lotsofproducts.py
    * Other Python libraries: httplib2, json, requests, random, string

Note: -- aplication, database_setup & lotsofproducts.py files are included in the project folder. Other Python libraries can be installed via pip (see relevant documentation for how to install). Follow the project info & description link to set up the linux VM.

To create the necessary datatables in Python, go to the project folder and:
    1. Run database_setup.py - this will create the database, tables & relationships between them
    2. Run lotsofproducts.py - this will populate the tables with example data

There is nothing further for the user to install.

3. Launch your favourite python IDE
4. Navigate to the project folder and run the application.py file
5. Launch an internet browser and navigate to http://localhost:8000
6. Explore the Snowboard Stores and their inventory
7. If you wish to add your own store log in via Google authentication so that you can access the relevant pages on the site.


### Notes & Acknowledgments

Users are able to navigate around the public areas of the site, but unable to alter records unless logged in.

The site uses Google authentication to login users.

Users may only amend Store / Product data that they created.

### JSON Endpoints

The following JSON endpoints are available for access to data from the app:

* All Stores Information: http://localhost:8000/stores/JSON
* Product Information for a Single Store: http://localhost:8000/stores/<Store_ID>/JSON
* Single Product of a Store Information: http://localhost:8000/stores/<Store_ID>/product/<Product_ID>/JSON


Thanks to the following sources for assistance with various elements of the project:
* [Udacity Full Stack Developer Course Notes](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004)
* [Python 2.7 Documentation](https://docs.python.org/2/index.html)
* [Udactiy Forums](https://discussions.udacity.com)
* [PostgreSQL Documentation](https://www.postgresql.org/docs/9.5/static/index.html)
* [Stackoverflow Forums](https://www.stackoverflow.com)
* [SQL Alchemy Documentation](http://docs.sqlalchemy.org/en/latest/)

______________________________________________________________________________

## PROJECT INFO & DESCRIPTION

[Link to Project Info](https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/348776022975462/lessons/3487760229239847/concepts/36269487530923)

### How will I complete this project?

This project is connected to the Full Stack Foundations and Authentication and Authorization courses, but depending on your background knowledge you may not need the entirety of both courses to complete this project. Here's what you should do:

1. Install Vagrant and VirtualBox
2. Clone the fullstack-nanodegree-vm
3. Launch the Vagrant VM (vagrant up)
4. Write your Flask application locally in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM).
5. Run your application within the VM (python /vagrant/catalog/application.py)
6. Access and test your application by visiting http://localhost:8000 locally

Get started with this helpful guide.
You can find the link to the fullstack-nanodegree-vm here.