"""
скрипт получения из SQL сервера dbfsv
данных для печати на ценниках, какие-то картинки
со способами ухода и гостами
"""
import pyodbc
from datetime import datetime
from typing import List, Tuple
from decouple import config



class Sql:
    def __init__(self, database, server="XXVIR00012,55000"):
        user_ace = config('ACE_user', None)
        pass_ace = config('ACE_pass', None)
        self.cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                                   "Server=" + server + ";"
                                   "Database=" + database + ";"
                                   "UID=" + user_ace + ";"
                                   "PWD=" + pass_ace + ";")
        self.query = "-- {}\n\n-- Made in Python".format(datetime.now()
                                                         .strftime("%d/%m/%Y"))

    def __call__(self, shk: Tuple = ('2631490420023',)):
        """
        2910240421214 - это закупной, он работать не должен
        2631490420023 - наш код, должен работать
        метод получения данных из базы данных ШП
        :return:
        """
        cursor = self.cnxn.cursor()
        inf_about_shk = dict()
        if len(shk) == 1:
            exec_string = f'SELECT max_iz, kod_sh_gl, gost, uhod_image, sost, i_d_izgot, sort, adres_sh, name, gr_tov, mod, razm, col_gl_txt, iz_nakl_ushk FROM ACE.dbo.View_max_iz_kod_sh_ushk where kod_sh_gl = {shk[0]}'
        else:
            exec_string = f'SELECT max_iz, kod_sh_gl, gost, uhod_image, sost, i_d_izgot, sort, adres_sh, name, gr_tov, mod, razm, col_gl_txt, iz_nakl_ushk FROM ACE.dbo.View_max_iz_kod_sh_ushk where kod_sh_gl in {shk}'
        try:
            cursor.execute(exec_string)
        except Exception as exc:
            print(exc)
            return inf_about_shk
        for row in cursor:
            inf_about_shk[int(row[1])] = {
                'gost': row[2].strip(),
                'care': row[3],
                'sost': row[4].strip(),
                'make_date': row[5].strip(),
                'sort': row[6],
                'adres_shp': row[7],
                'org': row[8].strip(),
                'gr_tov': row[9].strip(),
                'mod': row[10].strip(),
                'razm': row[11].strip(),
                'col_gl_txt': row[12],
                'iz_nakl_ushk': row[13],
                'russia': 'Произведено в России'
            }
        return inf_about_shk




def main():
    i_sql = Sql('ACE', server='192.168.2.234\DBF2008')
    l_shk = ('2714996306135', '2714996535139', '2835383535195', '2951298140337', '2714997306134', '2714997421134')
    gost = i_sql.manual(shk=l_shk)
    print(gost)

if __name__ == '__main__':
    main()