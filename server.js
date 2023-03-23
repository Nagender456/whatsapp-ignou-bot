import qrcode from 'qrcode-terminal';
import whatsappWeb from 'whatsapp-web.js';
const { LocalAuth, Client } = whatsappWeb;
import { spawn } from 'child_process';
import fs from 'fs';

const client = new Client({
	authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('Client is ready!');
});

const handleMessage = async (message) => {
	fs.writeFile('./currentMessage.txt', message.body, err => {
		if (err) {
			console.log(err);
		}
	})
	const python = spawn('python', ['main.py']);
	let dataToSend;
	python.stdout.on('data', (data) => {
		dataToSend = data.toString('utf8').split('|||');
	});
	python.on('exit', () => {
		if (dataToSend) {
			dataToSend.forEach(data => {
				const response = data.replace(/grey_tick_emoji/g, '☑️').replace(/green_tick_emoji/g, '✅').replace(/right_arrow/g, '▶️');
				message.reply(response);
			});
		}
	})
}

client.on('message', handleMessage);

// client.on('message_create', handleMessage);

client.initialize();
