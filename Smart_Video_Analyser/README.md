# child-rescue
The following tool was created to assist with eveidence collection during investigations

## Description
This project performs the following operations
 - Given a query image it searches for similar images in database
 - Given  an image  database it ouputs a csv file with objects corresponding to each image

 ## Instructions

 ### Setup
 clone the repo
 ```
 cd child-rescue
 ```
 create a  virtual env
```
conda create -n "room" python=3.10
conda activate room
```
 ```
 pip install -r requirements.txt
 ```
 ### GUI 
 run the following command to start a graphic interface. You can find the documentation for arguments in later section
 ```
 python src/main.py
 ```
![GUI_demo](GUI_demo.png)
 ### Image search

 - query: Path to input image (must be of jpg or png format)
 - k : Number of images similar to query to be extracted from the database.
 - data (Optional) : Path to folder containing all database images on which search operation needs to be performed. The images in this folder should be of  .jpg or .png format. Incase u have already created serach index using this databse which can be found in the "index folder path" then this field can be ignored. if no index folder path exists then data must be provoded for search.
 - index : path to folder where search index will be stored. this index basically helps with createing clip embeddings and clusters that will optmise the search process.
 - output: folder to store results i.e a csv file containing path to similar images. Total rows should match k
 
 ```
 python main.py search --query "image_file_path" --output "output folder path" --index "index-folder-path" --k <number of similar images to be retrieved and 0<k<50>> --data "images directory(optional)" 
 ```

 ### Object Detction

```
 python main.py detect --input "your input images directory path " --output "your output directory path"
 ```
