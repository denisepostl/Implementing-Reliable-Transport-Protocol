# Implementing-Reliable-Transport-Protocol
This repository is based on https://github.com/linxiaow/Implementing-Reliable-Transport-Protocol and allows sending an image using base64 encoding.

## OUTBOUND RECEIVER:
 - ./newudpl -vv -p 5001 -i "localhost/*" -o localhost:5003

## OUTBOUND SENDER:
 - ./newudpl -vv -p 5002 -i "localhost/*" -o localhost:5000 -O 80
 
## RECEIVER ARGUMENT
- python3 receiver.py --host localhost --port 5000 --dest_host localhost --dest_port 5001

## SENDER ARUGMENT
- python3 sender.py --host localhost --port 5003 --dest_host localhost --dest_port 5002 --timeout 2 --image_file image.jpg

### Documentation
A tiny Documention about the usage: [Documentation](https://github.com/denisepostl/Implementing-Reliable-Transport-Protocol/blob/main/Documentation.pdf)
