import Pusher from "pusher";

export const pusher = new Pusher({
  appId: "1990103",
  key: "de3222064318dd47db45",
  secret: "fb0846d219e17e884e81",
  cluster: "us3",
  useTLS: true,
});
