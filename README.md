# Trendyol Static Public API (Unofficial)

## API Reference

### Shipping Costs (shipping_costs.json)
- <https://frknltrk.github.io/trendyol_public_api/data/shipping_costs.json>

## Development

### To Do
- [x] schedule _etl.py_ to run on a weekly basis
- [ ] add more objects than just "shipping costs"

### Update & Upgrade
```bash
# Activate the virtual environment
$ source /path/to/venv/bin/activate

# Get a list of outdated packages
$ pip list --outdated

# Upgrade each package
$ pip install -U package_1 package_2 package_3 ...

# Save, at the very end:
# make sure everything works fine before this step
$ pip freeze --local > requirements.txt
```

### Resources
- <https://tymp.mncdn.com/prod/documents/engagement/kargo/guncel_kargo_fiyatlari.pdf>
- <https://tymp.mncdn.com/prod/documents/engagement/yasal_surecler/komisyon_vade_tablosu.pdf> (fees: will be implemented)
- <https://akademi.trendyol.com/satici-bilgi-merkezi/detay/109> (barem: will be implemented)

### Thanks
- <https://victorscholz.medium.com/hosting-a-json-api-on-github-pages-47b402f72603>
- <https://www.python-engineer.com/posts/run-python-github-actions/>
- <https://www.slingacademy.com/article/python-virtual-environment-how-to-upgrade-all-packages/>