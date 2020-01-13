# Semantic Frame Annotation Tool
We present an open-source web-based application with a responsive design for modular semantic
frame annotation (SFA). Besides letting experienced and inexperienced users do suggestion-based and slightly-controlled annotations,
the system keeps track of the time and changes during the annotation process and stores the users’ confidence with the current
annotation. Please test the tool at our website http://sfa.phil.hhu.de:8080/.

You can reuse the tool for your own purpose. If you do so, please cite our paper.

If you want to run the tool at your own computer, clone the github repository, move to the annotation_tool directory and run `python3 manage.py runserver`.
Currently there are two user accounts you can test: admin (password:guest123) and test (password:guest123).  
They have different permissions (reset and export database & only annotate).
The provided database contains the trial data of the SemEval 2019 Task 2: Unsupervised Lexical Semantic Frame Induction Task (see https://competitions.codalab.org/competitions/19159).

# Requirements
* install python3
* install pip from https://pip.pypa.io/en/stable/
from command line shoot
* install django with `pip install django`

# Citation

If you use SFA in your research, please cite SFA (Semantic Frame Annotation Tool)

@inproceedings{qasemizadeh-etal-2019-semeval,
    title = "{S}em{E}val-2019 Task 2: Unsupervised Lexical Frame Induction",
    author = "QasemiZadeh, Behrang  and
      Petruck, Miriam R. L.  and
      Stodden, Regina  and
      Kallmeyer, Laura  and
      Candito, Marie",
    booktitle = "Proceedings of the 13th International Workshop on Semantic Evaluation",
    month = jun,
    year = "2019",
    address = "Minneapolis, Minnesota, USA",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/S19-2003",
    doi = "10.18653/v1/S19-2003",
    pages = "16--30",
}


# How-to
  
## How to use the frontend from end user perspective
1) sign up 
2) choose a frame you want to change of the framelist
3) you now see a sentence with the chosen frame. 
    1) change the frame type with the radio buttons. Use the buttons next to the frame type to get a description of the type and examples.
    2) highlight selected core elements, childs of the frame verb and components of a multiword expression
    3) add a core element with a click on the token. Use the info icon to get the definition of the core element type.
    4) edit and delete the assigned core elements with a click on the core element.
    5) instead of adding a core element, add a multiword component related to the verb of the frame.
    6) delete the multiword component on click of it.
    7) (optional) add how certain you are about your annotation 
    8) (optional) add an comment to your annotation 
4) For further instructions read the paper or the annotation guidelines.

## How to use the frontend from admin perspective
   
1) create a new database
    1) delete the old database
    2) delete all files in the migrations directory (besides \_\_init\_\_.py)
    1) make sure that you have SQLITE3 installed to follow this tutorial.
    2) create a new empty database `sqlite3 my_database.sqlite3`
    3) adapt the database information (name, user, password, ...) in semeval/settings.py 
    4) run `python3 manage.py makemigrations annotate` and `python3 manage.py migrate` to get database structure
    5) create a superuser (admin) `python3 manage.py createsuperuser`, e.g., name: admin; password guest123
    6) start the local server `python3 manage.py runserver` and open the annotation tool in your favorite browser http://127.0.0.1:8000 (we recommend Firefox)
    7) You can log in with the superuser we created before or signup as a new user, e.g., test, using the signup button in the browser

2) Add FrameNet data to the database via the admin interface
    1) Log in as admin user
    2) Click on *To Admin Functions*
    3) Click on *insert frame net files* (First bullet point. This might take a while. You can see the progress in the command line window.)  
3) Add annotation records via the admin interface 
    1) specify the paths of your sentence files in *data/paramters.json*
    2) Click on *insert frame records* (third bullet point)
    3) select a text file, which contains records in the following format
    `#sentence_id verb_position verb.frame argument-:-argument-position-:-frameelement`, e.g., 
    `#20466020 24 drop.Change_position_on_a_scale stock-:-21-:-Item price-:-22-:-Attribute` (see data/gold/task-2.1.txt).
    If you would like to insert unannotated records, the following would be enough
    `#20466020 24 drop.UKN` (see data/test/task-1.txt). The example files are provided by the organizers of SemEval 2019 Task 2, see https://competitions.codalab.org/competitions/19159.
    4) assign users to frames. More than one user per frame is possible.
3) export data of the database
    1) export the annotated frames with "export annotated frames". Select which frames do you want and if the measured time and measured number of changes should be added to the data.
    2) export the history of a frame to see which steps the user took until his final decision and how long the took until it.

## How to change the backend
* If you do not know django, we recommend this tutorial https://tutorial.djangogirls.org/en/.
* If you like to deploy the annotation tool, please see *deploy_django.txt* and https://docs.djangoproject.com/en/2.2/howto/deployment/

# License
* The code of the tool is licensed under the MIT license. If use this code please cite our paper.    
    


