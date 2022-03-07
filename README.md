# OSUSUME
#### Video Demo: https://youtu.be/-SWl38ulunk
#### Description:
Osusume ( which means recommendation in japanese) is a simple web app developed using the Flask framework. It is an application in which users can receive recipe recommendations tailored to them based on their cuisine preferences and overall daily spending budget. This project was created using the flask python framework in tandem with CSS, HTML Javascript and SQLite.

#### Additional Setup Requirements:
Other than the dependecies provided in the requirements.txt file you will need to create a free account to accesss the Spoonacular API https://spoonacular.com/food-api/console#Dashboard. Upon login go to your Profile tab and their you can get your API key. Next up you can create an .env file in your IDE and create the APIKEY variable with your newly generated key as the value.
#### Usage
##### Registration:
The user will be routed to the login page upon accessing the application. From there they can login with a previously created account or create a new one. Upon registration the user is prompted to create a username and password as well as confirming the password entered. Next the user can set their intial cuisine preferences, they can select from multiple types from a list of over 25 different types of cuisines. Finally to complete the registration process they can select their current daily budget.
##### Main Functions:
On the main page the user is provided with 2 random suggestions that meet the criteria of their currently set preferences. From their you can select either one of those recipes to view their details. Also on the main page their is a suggestions button that upon pressing will provide you with a larger list of suggestions based off of your preferences. On the navigation bar there is also the option to do a general search if you have a specific type of dish that you are searching for.

On the right side of the navigation bar the username is displayed with a drop-down menu that provides two options, Settings and Reset Password. The first option allows the user to change their current cuisines preferences and daily budget if they are in the mode for changing things up. Lastly the reset password option works exactly as described. The user confirms their current password and then can change to a new password.


#### Notes on functionality
This project uses the Spoonacular API for all of its recipe data. I originally wanted to use the Edamam API because they do have a larger library of recipes than Spoonacular. However, the meta data on the recipes of Edmama are a bit consistent which made it difficult to stream line some standards for displaying data. Spoonacular's metadata was always consistent from each API call.

So using this API I was able to create custom functions that grab all the neccessary data that is displayed in the application. These functions are then called in the Flask app.py file in multiple instances on several of the established routes.
#### Future Ideas/Additions
In the next iteration of the application I would like to definetly clean up the UI and make it a bit more robust and eye catching. I would like to add a Favorites feature which whenever a user hits the favorite button a recipe it will be added to a list view of the current users favorites on the main page. Next up would be a rating system where users can simple choose between 1 and 5 stars on a recipe. Following that would be an option to share the recipe externally using social media or email. Lastly would be the integeration of some sort of points system that would distribute different set of points based on the previously mentioned new features. So whenever a user performs one of those actions they will be awarded points. The next thing i will need to brainstorm is what to allow the user to do with those points.

