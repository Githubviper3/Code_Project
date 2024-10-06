def Lencheck(password):
  return [True,True] if len(password) >= 6 else [False, "Must be 6 Characters or more long"]

def Uppercheck(password):
  return [True,True] if any(i.isupper() for i in password) else [False, "No Uppercase Letters"]

def Lowercheck(password):
  return [True,True] if any(i.islower() for i in password) else [False, "No Lowercase Letters"]

def SpcCheck(password):
  return [True,True] if password.isalnum() is False else [False, "No Special Characters"]

def Numcheck(password):
  return [True,True] if any(i.isdigit() for i in password) else [False, "No Numbers"]

def paswordcheck(password):
  checks1= [Lencheck(password)[0],Uppercheck(password)[0],Lowercheck(password)[0],SpcCheck(password)[0],Numcheck(password)[0]]
  checks1 = all(checks1)
  checks2= [Lencheck(password)[1], Uppercheck(password)[1], Lowercheck(password)[1], SpcCheck(password)[1], Numcheck(password)[1]]
  endmessage = []
  for i in checks2:
    if isinstance(i,str):
      endmessage.append(i)

  if checks1:
    return [True,True]
  else:
    return [False,endmessage]
