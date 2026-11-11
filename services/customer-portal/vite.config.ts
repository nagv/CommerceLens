import {defineConfig} from 'vite';
export default defineConfig({server:{proxy:{'/api/notifications':'http://127.0.0.1:8085','/api':'http://127.0.0.1:8080'}}});
