import Pusher from "pusher-js";

const pusherClient = new Pusher(process.env.NEXT_PUBLIC_PUSHER_APP_KEY!, {
  cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER!,
});

// Add connection debugging
pusherClient.connection.bind('connected', () => {
  console.log('Pusher connected');
});

pusherClient.connection.bind('disconnected', () => {
  console.log('Pusher disconnected');
});

pusherClient.connection.bind('error', (error: unknown) => {
  console.error('Pusher connection error:', error);
});

export default pusherClient;
