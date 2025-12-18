**Streamlit:**
All the user interface and design was created utilizing python and streamlit over the usual react / javascript. This was done as a majority of our projects are created in python and so I thought it would be better to keep with that trend rather than force other members to learn javascript, css, react, when the job doesn't require it. In addition, with github, we should be able to do streamlit community (not done yet). 

**States:**
Similar to REACT, everytime you interact with any button / feature in Streamlit, the whole webpage refreshes including the code. This means that all of the variables will restart. As a result, if you need to store something across multiple refresh, you should store it in a state as these persist throughout all the interactions. Here is an example: 

<div align="center">
    <img width="296" height="113" alt="image" src="https://github.com/user-attachments/assets/29b8e313-f209-4efd-b18c-931b36cba5d0" />
</div>

Defense and Plantiff states are arrays that store which questions need to be recoded based on the fact that they were highlighted.

Recode Setting is a dictionary that stores a string as a key and then another dictionary holding all the recode values as an element: dict[str, dict[str, int]]. It will look something like this if that was confusing: 
<div align = "center">
  <img width="179" height="122" alt="image" src="https://github.com/user-attachments/assets/5fbb1766-99c4-4918-9e56-8d602f7aac45" />
</div>
