# ProjectMota2
#### Video Demo: [watch here on YouTube](https://youtu.be/VkG5f3NflDc)
#### Description:
This is a web application useful for calculating & storing your and your family's height, weight and body mass index or BMI. This project intends to encouraging the user to make healthy decisions and be conscious of their diet to improve their quality of life and health. BMI is one of the important measures of bone, muscle and tissue fitness. The BMI category ranges vary between European and Asian criteria. Since the Asian standard has vaster categories, ProjectMota2 uses it for categorizing the collected data.
## Layout
- Register
- Log In
- Update
    - Personal
        - Update
    - Family Details
        - Update
        - Add New Members
        - Remove Existing Members
- Dashboard
    - Personal
    - Family
- Check BMI
## List of Pages
#### Register
This is a registration page where one can easily sign up for a new account. This will redirect to update personal details page.
#### Log In
You can log into your account here. On successful log in, you will be redirected to the personal dashboard. This is also our first page.
#### Update
This menu links to all pages for updating personal and family details. Each update page allows the user to input data in either metric or imperial units. However, the data is finally stored in metric units, i.e, in kgs and cms.
###### Update Personal Details
Here, the user can update his height and weight. This page redirects the user to the index page or the personal dashboard. The BMI will be calculated instantly and would be shown on the index page.
###### Update Family Details
This page is used to change the height and weight of the selected family member.
###### Add New Members
Here, one can add the new family members by entering their name, weight and height.
###### Remove Existing Members
Here, one can delete the data of their family members if needed. This page, in particular, asks for a confirmation before deleting, thus preventing accidental changes and data loss.
#### Dashboard
This navigation bar menu links the user to the two of the following dashboards.
###### Personal Dashboard
This page contains has user's data, i.e, height in centimeters, weight in kilograms, date and time of last update, BMI and BMI category. This page shows up on successful log in. It is the index page of our project.
###### Family Dashboard
This page tabulates the data of user's family members. Both of the dynamically generated dashboards display data in metric units.
#### Check BMI
The BMI or Body Mass Index is defined as the body mass divided by the square of the body height, with the unit of kg per sq. m. This is an interactive page which allows you to check your BMI without making any changes to the database. A colour-coded display then shows your BMI as per the categories: Underweight, Normal, Overweight, Obese with respect to the Asian BMI standard.
## Security and Data Privacy
The session data is stored on the top of cookies and signed by the server cryptographically. Flask has been used to track the session data. The user's password is secured using Werkzeug. Session data is cleared on logging out successfully or once the server is turned off. Any data you entered for storage is completely private and visible only to you when logged in. No data is shared with or sold to any third-party.
## Programming Technologies used
- Python
- HTML
- SQLite
- JavaScript
- Cascading Style Sheets
- Flask
- Flask sessions
- Werkzeug
- Jinja
- BootStrap
- CS50 library for SQLite3


Based on [Mashhood Alam's](https://github.com/MASHOD0) [ProjectMota](https://github.com/MASHOD0/ProjectMota)


Developed by [Aieshah Nasir](https://github.com/aie007) as CS50 Final Project - CS50x2021
