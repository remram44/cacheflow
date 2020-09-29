export function sortByKey<T>(array: T[], key: (value: T) => {}) {
  array.sort((a, b) => {
    if (key(a) < key(b)) {
      return -1;
    } else if (key(a) > key(b)) {
      return 1;
    } else {
      return 0;
    }
  });
}
