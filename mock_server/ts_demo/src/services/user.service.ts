import { User } from "../models/user";

export class UserService {
  private users: User[] = [
    { username: "admin", password: "123456" }
  ];

  register(user: User): boolean {
    const exist = this.users.find(u => u.username === user.username);
    if (exist) return false;
    this.users.push(user);
    return true;
  }

  login(username: string, password: string): boolean {
    return this.users.some(
      u => u.username === username && u.password === password
    );
  }

  list(): string[] {
    return this.users.map(u => u.username);
  }

  delete(username: string): boolean {
    const before = this.users.length;
    this.users = this.users.filter(u => u.username !== username);
    return this.users.length < before;
  }
}

export const userService = new UserService();