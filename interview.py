import requests
from bs4 import BeautifulSoup
import openai
import os 


# define the env variable 
api_key = os.getenv("OPENAI_API_KEY")
# define the openAI API with the api key we set in the env variable 
client = openai.OpenAI(api_key=api_key)


# Define a function to use GPT-4 to split the text into smaller chunks based on the max length provided.
def gpt4_split_text(text, link, max_length=750):
    print("In gpt4_split_text for ", link)

    messages = [
        {
            "role": "system",
            "content": "You are an assistant that helps split articles into smaller chunks while preserving context, headers, paragraphs, and lists."
        },
        {
            "role": "user",
            "content": f"Split the following text into chunks of roughly {max_length} characters while preserving context, headers, paragraphs, and lists. Do not merge words and remove necessary spaces.:\n\n{text}"
        }
    ]


    # API Call to OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=4096,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    print("After GPT chunking")
    return  response.choices[0].message.content.strip().split("\n\n")


def getWebpageChunks():

  # URL for the help page 
  url = 'https://www.notion.so/help'
  response = requests.get(url)

  # return array with all of the chunked pages 
  retArr = []

  if response.status_code == 200:
      # Use BeautifulSoup to parse through the html page
      soup = BeautifulSoup(response.content, 'html.parser')

      links = []
      ret = {}

      # Using the <a> tags, get all of the URLS for all of the links 
      for a_tag in soup.find_all('a', href=True):
          links.append(a_tag['href'])

      # Get all of the hyper links 
      for link in set(links):
          # make sure the link is from the /help page 
          if "/help" in link:

            # construct the link 
            responseLink = requests.get("https://www.notion.so"+link)
            if responseLink.status_code == 200:

              # parse the individual links 
              soupLink = BeautifulSoup(responseLink.content, 'html.parser')

              # get the text on the webpage 
              text = soupLink.get_text()

              # call the LLM model to split the text on the webpage according to the requirements 
              # also create a hashmap to store the chunks associated with a webpage in case we need to access later
              # looks like hashmap = {link: [chunk1,chunk2,chunk3], link2: [chunk1,chunk2]}
              ret[link] = gpt4_split_text(text, link, max_length=750)

              # append the chunks of the particular webpage to a return array
              # structure of the return array is one large array with smaller arrays inside with the chunks for each webpage 
              # retArr = [[webpage 1 chunk1, chunk2, chunk3], [webpage2 chunk1, chunk2]]
              retArr.append(ret[link])
              
      return retArr

# failed to get the inital notion webpage 
  else:
      print(f"Failed to retrieve the page. Status code: {response.status_code}")    
      
      
      
ret = getWebpageChunks()


