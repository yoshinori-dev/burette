<html>
<head><title>TITLE!</title></title>
<body>
hogehoge body
LOOP
{% for user in users %}
  <div><a href="{{ user.url }}">{{ user.name }}</a></div>
{% endfor %}
</body>
</html>
