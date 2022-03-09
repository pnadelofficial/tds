import re
import pandas as pd
pd.set_option('display.max_rows', 500)
import glob

def splitEmails(file_path):
  ### By file_path, I mean a string like this: 'data/Staff_*_djvu.txt'.
  ### As we make the parser more robust, we can start using the entire data directory.
  email_text = ''
  
  for file in list(glob.glob(file_path)):
    with open(file, encoding='utf8') as email_file:
      email_text = email_text + email_file.read()

  email_re = r"(?<=From:\s)(.*?)(From:)" 
  email_list = re.findall(email_re, email_text, re.DOTALL) 
  ### This regex method splits the long string of all the emails into "documents" by breaking it at each instance of "From:"
  ### This method should be updated as we are missing the last email because there is no "From:" below it.
  return email_list

## Below are the functions I wrote to parse and start to clean the text. 
## Generally, the emails follow this form:
## From:
## Sender, Name
## Sent: 
## Date
## To:
## Recipient, Name
## Cc:
## Cc, Name; Another, Cc; etc...
## Subject:
## Subject line
## (Sometimes: Attachments:
## SomeAttachment.aht)
## Body of the email.
def extractFrom(raw_email):
  from_re = r"(.*?)(?=Sent:)"
  ### Searches for the line above the "Sent:" line. 
  from_search = re.search(from_re, raw_email, re.DOTALL)
  if from_search:
    return from_search.group().strip()
  else:
    from_re2 = r"(.*?)(?=Date:)"
    ## Another variant: one where "Sent:" is replaced with "Date:" (different email platform, different format -- maybe)
    from_search2 = re.search(from_re2, raw_email, re.DOTALL)
    if from_search2:
      return from_search2.group().strip()
    else:
      return None

def extractDate(raw_email):
  sent_re = r"(?<=Sent:)(.*?)(?=To:)"
  ### Searches for the line in between "Sent:" and "To:" 
  sent_search = re.search(sent_re, raw_email, re.DOTALL)
  if sent_search:
    return sent_search.group().strip()
  else:
    date_re = r"(?<=Date:)(.*?)(?=To:)"
    ### As above, sometimes the "Sent:" line is "Date:", instead
    date_search = re.search(date_re, raw_email, re.DOTALL)
    if date_search:
      return date_search.group().strip()
    else:
      return None

def extractTo(raw_email):
  to_re = r"(?<=To:)(.*?)(?=Cc:)"
  ### Searches for the line in between "To:" and "Cc:"
  to_search = re.search(to_re, raw_email, re.DOTALL)
  if to_search:
    return to_search.group().strip()
  else:
    return None

def extractCc(raw_email):
  cc_re = r"(?<=Cc:)(.*?)(?=Subject:)"
  ### Search for the line in between "Cc:" and "Subject:"
  cc_search = re.search(cc_re, raw_email, re.DOTALL)
  if cc_search:
    return cc_search.group().strip()
  else:
    return None

def extractSubject(raw_email):
  subject_re = r"(?<=Subject:)(\s*)[^\n]+"
  ### Searches for the line below "Subject:"
  subject_search = re.search(subject_re, raw_email, re.DOTALL)
  if subject_search:
    return subject_search.group().strip()
  else:
    return None

def extractBody(raw_email, subject):
  body_re = r"(?<=Subject:)(.*)"
  ### Searches for the whole text from after "Subject:", as a result we have to get rid of one line below "Subject:."
  ### So I removed it with replace().   
  body_search =  re.search(body_re, raw_email, re.DOTALL)
  if body_search:
    return body_search.group().replace(subject, '').strip()
  else:
    return None

## Other times, the emails follow another form:
## From:
## Sent: 
## To:
## Cc:
## Subject:
## (Sometimes: Attachments:)
## Sender, Name
## Subject line
## Date
## Recipient, Name
## Cc, Name; Another, Cc; etc...
## (SomeAttachment.aht)
## Re:
## Body of the email.
def formatDF(raw_email):
  format_check_string = "\n\nSent: \nTo:"
  ### Checks what format the email is in 
  if raw_email.startswith(format_check_string):
    p = "(?<=Subject:)(.*)(?=Re:)[^\n]+"
    ### Searches for lines in between "Subject:" and "Re:"
    p_search = re.search(p, raw_email, re.DOTALL)
    if p_search:
      from_line = p_search.group().strip().split('\n')[0]
      sent_line = p_search.group().strip().split('\n')[2]
      to_line = p_search.group().strip().split('\n')[3]
      cc_line = p_search.group().strip().split('\n')[5]
      subject_line = p_search.group().strip().split('\n')[6]
      ### Splits up all of the lines
      body_re = "(?<=Re:)(.*)"
      ### Searches for lines after "Re:"
      body_search = re.search(body_re, raw_email, re.DOTALL)
      if body_search:
        body = body_search.group().replace(subject_line, '').strip()
      else:
        body = None 
    else:
      ### Default values if the parser breaks, as we have to dropna() once it is formated into the DF 
      from_line = None
      sent_line = None
      to_line = None
      cc_line = None
      subject_line = None
      body = None 
  else:
    ### Calling all of the functions above
    from_line = extractFrom(raw_email)
    sent_line = extractDate(raw_email)
    to_line = extractTo(raw_email)
    cc_line = extractCc(raw_email)
    subject_line = extractSubject(raw_email)
    body = extractBody(raw_email, subject_line)

  return from_line, sent_line, to_line, cc_line, subject_line, body

def createDF(file_path):
  ### Same file_path form above, input into the splitEmails
  email_df = pd.DataFrame(data=splitEmails(file_path))
  email_df = email_df.drop(columns=[1])
  ### I had a hard time using apply to get out all of the data 
  email_df['parsed'] - email_df[0].apply(formatDF)
  email_df[['From', 'Sent', 'To', 'Cc', 'Subject', 'Body']] = pd.DataFrame(email_df['parsed'].tolist(), index=email_df.index)
  return email_df
