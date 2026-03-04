# Python JPEG Carving

<p>inspired by this <a href="https://codeonby.com/2022/05/07/python-for-data-recovery/">article</a></p>

a simple JPEG carving script, that scans bytes for JPEG`s signatures (the magic bytes)

### Usage (Linux)
```bash
sudo python main.py /dev/sdX ~/location_on_your_machine/
```

### AI Analyze usage (Linux)
```bash
sudo python analyze_recovered.py ./local_pasta_recuperados
```
after that, u should see an analise.jsonl inside the folder passed at the first arg


this is just an assignment for college
