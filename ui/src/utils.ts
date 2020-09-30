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

const CHARACTERS =
  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

export function randomString(length: number): string {
  let result = '';
  for (let i = 0; i < length; ++i) {
    result += CHARACTERS.charAt(Math.floor(Math.random() * CHARACTERS.length));
  }
  return result;
}
