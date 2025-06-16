import Pusher from "pusher-js";

const pusherClient = new Pusher(process.env.NEXT_PUBLIC_PUSHER_APP_KEY!, {
  cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER!,
});

// Add comprehensive connection debugging
console.log('Pusher client configuration:', {
  key: process.env.NEXT_PUBLIC_PUSHER_APP_KEY ? 'CONFIGURED' : 'MISSING',
  cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER ? process.env.NEXT_PUBLIC_PUSHER_CLUSTER : 'MISSING'
});

pusherClient.connection.bind('connected', () => {
  console.log('✅ Pusher connected successfully');
});

pusherClient.connection.bind('connecting', () => {
  console.log('🔄 Pusher connecting...');
});

pusherClient.connection.bind('disconnected', () => {
  console.log('❌ Pusher disconnected');
});

pusherClient.connection.bind('unavailable', () => {
  console.log('❌ Pusher unavailable');
});

pusherClient.connection.bind('failed', () => {
  console.log('❌ Pusher connection failed');
});

pusherClient.connection.bind('error', (error: unknown) => {
  console.error('❌ Pusher connection error:', error);
});

export default pusherClient;
