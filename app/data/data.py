import ast
from collections import defaultdict
class Story:
    def __init__(self, sid, title = "", text = "", author = ""):
        self.id = sid
        self.title = title
        self.text = text
        self.author = author

    def to_dict(self):
        res = {}
        res["id"] = self.id
        res["title"] = self.title
        res["text"] = self.text
        return res

def read_stories(skip = 14933):
    author_stories = defaultdict(list)
    stories_text = {}
    with open("stories") as f:
        i = 0
        for i in range(skip):
            f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            line = line.replace(':true',':True')
            line_dict = ast.literal_eval(line)
            author = line_dict.get("by")
            if not author or ("deleted" in line_dict):
                i += 1
                continue
            title = line_dict.get("title")
            text = line_dict.get("text")
            if not title:
                print("warning: %d has no title, id: %s" % (i, line_dict["id"]))
            if not author:
                print("warning: %d has no author, id: %s" % (i, line_dict["id"]))
                i += 1
                continue
            story = Story(line_dict["id"], title, text)
            author_stories[line_dict["by"]].append(story.to_dict())
            i += 1
        print("read %d lines." % i)
    with open("author.txt", "w") as f:
        for author in author_stories:
            f.write(str({"author":author, "story":author_stories[author]}))
            f.write("\n")


if __name__ == "__main__":
    read_stories()
