*Please :star: this repo if you find it useful*

#Saures custom component for Home Assistant

## Installation

1. Open the directory for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `saures`.
4. Download files from this repository.
5. Place the files you downloaded in the new directory `saures` you created.
6. Restart Home Assistant

## Configuration

```yaml
# Example configuration.yaml entry
saures:
  username: demo@saures.ru
  password: demo
```
#### Configuration Variables

**name:**\
  _(string) (Optional)_\
  Name to use in the frontend.\
  _Default value: Saures_
  
**username:**\
  _(string) (Required)_\
  User name (Saures server).\
  
  **password:**\
  _(string) (Required)_\
  Password name (Saures server).\
  
  <p align="center">* * *</p>
Saures server responds very slowly. Therefore, you will most likely see Home Assistant warnings that setup and update of platform is taking more then 10 secods. This is my first attempt at programming and I cannot guarantee stable operation.
<p align="center"><br>
