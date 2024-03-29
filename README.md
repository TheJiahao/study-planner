# Study-planner

[![codecov](https://codecov.io/gh/TheJiahao/study-planner/branch/main/graph/badge.svg?token=VSQHAACB32)](https://codecov.io/gh/TheJiahao/study-planner)

[Uusin release](https://github.com/TheJiahao/ohte-harjoitustyo/releases/latest)

Sovellus tuottaa aikataulun opinnoille annettujen vaatimusten perusteella.

![Kuva sovelluksesta](dokumentaatio/kuvat/aikataulunakyma.png)

## Dokumentaatio

- [Käyttöohje](dokumentaatio/kaytto-ohje.md)
- [Vaatimusmäärittely](dokumentaatio/vaatimusmaarittely.md)
- [Arkkitehtuurikuvaus](dokumentaatio/arkkitehtuuri.md)
- [Testausdokumentti](dokumentaatio/testausdokumentti.md)
- [Työaikakirjanpito](dokumentaatio/tyoaikakirjanpito.md)
- [Changelog](dokumentaatio/changelog.md)

## Asennus ja käynnistys

1. Asenna Python `3.10.x` ja [Poetry](https://python-poetry.org/).
2. Klonaa repositorio.
3. Asenna riippuvuudet:

    ```shell
    poetry install
    ```

4. Käynnistä sovellus:

    ```shell
    poetry run invoke start
    ```

## Invoke-tehtävät

Suorita komennot projektin juurihakemistossa.

### Testaus

```shell
poetry run invoke test
```

### Kattavuusraportti

```shell
poetry run invoke coverage-report
```

### Pylint

```shell
poetry run invoke lint
```

### Koodin formatointi

```shell
poetry run invoke format
```
