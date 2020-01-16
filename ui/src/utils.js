export function sortByKey(array, key) {
  array.sort(function(a, b) {
    if(key(a) < key(b)) {
      return -1;
    } else if(key(a) > key(b)) {
      return 1;
    } else {
      return 0;
    }
  });
}

// https://stackoverflow.com/a/2117523
export function uuid4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
