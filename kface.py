import os
import redis
import pickle
import face_recognition


class Kface:

    def __init__(self):
        self.known = []
        self.knowns_name = []
        self.rc = redis.Redis(os.getenv('REDIS', '127.0.0.1'))
        self.knowns_path = os.getenv('KNOWNS_FOLDER', './known')
        self.upload_path = os.getenv('UPLOAD_FOLDER', './uploads')
        self.populeate_from_redis()
        self.populate_knows()
        self.tolerance = float(os.getenv('TOLERANCE', '0.56'))

    def populate_knows(self):
        for f in os.listdir(self.knowns_path):
            file = os.path.join(self.knowns_path, f, self.knowns_path)
            if os.path.isfile(file):
                self.get_or_set(f)
        for f in os.listdir(self.upload_path):
            file = os.path.join(self.upload_path, f, self.upload_path)
            if os.path.isfile(file):
                self.get_or_set(f)

    def populeate_from_redis(self):
        self.known = []
        self.knowns_name = []
        self.knowns_files = []
        for key in self.rc.scan_iter("name:*"):
            self.known.append(pickle.loads(self.rc.get(key)))
            key_d = key.decode().split(':')[1]
            if len(key_d.split("|")) > 1:
                name, filename  = key_d.split("|")
                self.knowns_name.append(name)
                self.knowns_files.append(filename)
            else:
                self.knowns_name.append(key_d)
                self.knowns_files.append(key_d)

    def get_or_set(self, file_name, path, name=None):
        if not name:
            name = file_name.split(".")[0]
        self.knowns_name.append(name)
        self.knowns_files.append(name)
        p_arr = self.rc.get('name:{}|{}'.format(name, file_name))
        if p_arr:
            self.known.append(pickle.loads(p_arr))
            return
        file = os.path.join(path, file_name)
        image = face_recognition.load_image_file(file)
        image_encode = face_recognition.face_encodings(image)[0]
        self.rc.set('name:{}|{}'.format(name, file_name), pickle.dumps(image_encode))
        self.known.append(image_encode)

    def match_face(self, file, path):
        img = face_recognition.load_image_file(os.path.join(path, file))
        face_locations = face_recognition.face_locations(img)
        face_encodings = face_recognition.face_encodings(img, face_locations)
        face_names = []
        face_locations_found = []
        n = 0
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known, face_encoding, tolerance=self.tolerance)
            name = "Unknown"
            if True in matches:
                nn = 0
                for m in matches:
                    if m:
                        name = self.knowns_name[nn]
                        face_names.append(name)
                        face_locations_found.append(face_locations[n])
                    nn = nn + 1
            else:
                face_names.append(name)
                face_locations_found.append(face_locations[n])
            n = n + 1
        return {
            "names": face_names,
            "locations": face_locations_found,
            "upload_file": file
        }

    def print_names(self):
        for face in self.knowns_name:
            print(face, self.known[self.knowns_name.index(face)])

    def return_names(self):
        return self.knowns_name


if __name__ == "__main__":
    face = Kface()
    face.print_names()
    print(face.match_face('obama.jpeg', 'test'))
    face.get_or_set('obama.jpeg', 'test', 'Obama Forsti')
