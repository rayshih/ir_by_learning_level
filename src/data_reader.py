import json

def loadJL(filename):
  data = []

  with open(filename) as fp:
    for line in fp:
      line.strip()
      item = json.loads(line)
      data.append(item)

  return data
