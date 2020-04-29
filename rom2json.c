#include <stdio.h>
#include <stdlib.h>

int levels[] = { 0x18a00, 0x18f00, 0x19080 };

uint8_t *rom;
FILE *fcsv;
FILE *fcsvextra;
FILE *fjson;

int readlevel(int level) {
int tipoBloque;
int lgtudX;
int lgtudY;

int altura;
int posX;
int posY;
long pun = 0;

int alt, xx, yy;

    pun = levels[level] + 0x4000;
    // printf ("Pun ( %lx : %ld ) Dato ( %X : %u ) \n", pun, pun, rom[pun], rom[pun]);
    while ((int) (rom[pun]) != 0xff){
      tipoBloque = rom[pun];
      //  printf ("Position: %lx --> %d \n", pun, rom[pun]);
      if (((tipoBloque & 0x07) == 0) || ((tipoBloque & 0x07) >= 6)) {
        printf("Invalid block type at rom (%lx:%02X) tipoBloque (%02X) & 0x07 -> %d \n", pun, rom[pun], tipoBloque, tipoBloque & 0x07);
        break;
      }
      lgtudX = rom[pun+3];
      lgtudY = rom[pun+4];
      // si la entrada no es de 5 bytes, la longitud se codifica en 4 bits en vez de en 8¬
      if ((tipoBloque & 0x08) == 0){
        lgtudY = lgtudX & 0x0f;
        lgtudX = (lgtudX >> 4) & 0x0f;
      }

      altura = (tipoBloque >> 4) & 0x0f;
      posX = rom[pun+1];
      posY = rom[pun+2];

      lgtudX++;
      lgtudY++;

      if ((posX >= 0x70 && posX <= 0xC0) && (posY >= 0x70 && posY <= 0xC0)) {
        printf ("level %d posX %d posY %d high %d lgtudX %d lgtudY %d\n", level, posX, posY, altura, lgtudX, lgtudY);

        fprintf (fcsv, "%d,%d,%d,%d,%d,%d\n", level, posX, posY, altura, lgtudY, lgtudX);
        // avanza a la siguiente entrada¬

        for (xx = 0; xx < lgtudX; xx++) {
          for (yy = 0; yy < lgtudY; yy++) {
            for (alt = 0; alt <= altura && alt < 12; alt++) {
                fprintf (fcsvextra, "%d,%d,%d,%d\n", level, posX+xx, posY+yy, alt);
            }
          }
        }
      }

      if ((tipoBloque & 0x08) == 0){
        pun += 4;
      } else {
        pun += 5;
      }
    }
  return 0;
}

int main(int argc, char** argv) {
  long ii;
  FILE *f = fopen("rom", "rb");

  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  fseek(f, 0, SEEK_SET);  /* same as rewind(f); */

  rom = malloc(fsize + 1);
  fread(rom, 1, fsize, f);
  fclose(f);

  fcsv = fopen ("files/alturas.csv", "w");
  fprintf (fcsv, "Level,X,Y,height,lenX,lenY\n");

  fcsvextra = fopen ("files/alturas-extra.csv", "w");
  fprintf (fcsvextra, "Level,X,Y,height\n");

  fjson = fopen ("files/alturas.json", "w");

  for (ii=0 ; ii <3 ; ii++)
    readlevel(ii);

  fclose (fcsv);
  fclose (fcsvextra);
  fclose (fjson);

	return 0;
}
