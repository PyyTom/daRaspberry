import flet as fl,sqlite3
from PIL import ImageGrab
db=sqlite3.connect('db.db')
db.execute('create table if not exists CONFIGS(CONFIG,N integer,PIN,PLUG)')
db.close()
left=['3.3','G02 - I2C1 SDA','G03 - I2C1 SCL','G04','GND','G17','G27','G22','3.3','G10 - SPI0 MOSI','G09 - SPI0 MISO','G11 - SPI0 SCLK','GND','RES','G05','G06','G13','G19 - SPI1 MISO','G26','GND',]
right=['5.0','5.0','GND','UTX','URX','G18','GND','G23','G24','GND','G25','G08 - SPI0 CS0','G07 - SPI0 CS1','RES','GND','G12','GND','G16 - SPI1 CS0','G20 - SPI1 MOSI','G21 - SCLK']
def main(page:fl.Page):
    page.window_full_screen=True
    page.theme_mode=fl.ThemeMode.LIGHT
    dialog = fl.AlertDialog()
    page.dialog = dialog
# POPULATING PINS COLUMNS
    c_l_pins,c_r_pins,c_l_plugs,c_r_plugs=fl.Column(height=800),fl.Column(height=800),fl.Column(height=800),fl.Column(height=800)
    c=1
    for n in range(len(left)):
        color='black'
        if left[n]=='3.3':bg='yellow'
        elif left[n]=='GND':bg,color='black','white'
        elif left[n]=='RES':bg='grey'
        else:bg='orange'
        c_l_plugs.controls.append(fl.TextField(label=str(c),width=400,height=31))
        c_l_pins.controls.append(fl.TextField(left[n],read_only=True,width=200,height=31,bgcolor=bg,color=color))
        c+=2
    c=2
    for n in range(len(right)):
        color='black'
        if 'U' in right[n]:bg='green'
        elif right[n]=='GND':bg,color='black','white'
        elif right[n]=='5.0':bg='red'
        elif right[n]=='RES':bg='grey'
        else:bg='orange'
        c_r_pins.controls.append(fl.TextField(right[n],read_only=True,width=200,height=31,bgcolor=bg,color=color))
        c_r_plugs.controls.append(fl.TextField(label=str(c), width=400, height=31))
        c+=2
    def update():
        d_configs.options=[fl.dropdown.Option('NEW')]
        db=sqlite3.connect('db.db')
        for config in db.execute('select CONFIG from CONFIGS group by CONFIG ').fetchall():d_configs.options.append(fl.dropdown.Option(config[0]))
        db.close()
        page.update()
    def save(e):
        if t_config.value=='':
            dialog.title=fl.Text("CONFIGURATION'S NAME IS REQUIRED")
        else:
            l,r=0,0
            db = sqlite3.connect('db.db')
            for n in range(1,41):
                if n%2==0:
                    db.execute('insert into CONFIGS values(?,?,?,?)',((t_config.value).upper(),n,c_r_pins.controls[r].value,(c_r_plugs.controls[r].value).upper(),))
                    r+=1
                else:
                    db.execute('insert into CONFIGS values(?,?,?,?)',((t_config.value).upper(),n,c_l_pins.controls[l].value,(c_l_plugs.controls[l].value).upper(),))
                    l+=1
                db.commit()
            db.close()
            dialog.title = fl.Text("CONFIGURATION CORRECTLY SAVED")
            update()
        dialog.open = True
        page.update()
    def printer(e):
        if t_config.value=='':
            dialog.title=fl.Text("CONFIGURATION'S NAME IS REQUIRED")
        else:
            ss=ImageGrab.grab()
            ss.save(t_config.value+'.png')
            ss.show()
            dialog.title = fl.Text("CONFIGURATION CORRECTLY PRINTED")
        dialog.open = True
        page.update()
    def load(e):
        if d_configs.value=='NEW':
            t_config.value,t_config.disabled='',True
            for plug in c_r_plugs.controls:
                plug.value=''
                page.update()
        else:
            t_config.value=d_configs.value
            l,r=0,0
            db = sqlite3.connect('db.db')
            for n in range(1,41):
                if n%2==0:
                    c_r_plugs.controls[r].value=db.execute('select PLUG from CONFIGS where CONFIG=? and N=?',(t_config.value,n)).fetchone()[0]
                    r+=1
                else:
                    c_l_plugs.controls[l].value = db.execute('select PLUG from CONFIGS where CONFIG=? and N=?',(t_config.value, n)).fetchone()[0]
                    l += 1
                page.update()
            db.close()
    d_configs=fl.Dropdown(label='CONFIGURATIONS',on_change=load)
    t_config=fl.TextField(label='CONFIGURATION',disabled=True)
    update()
    page.add(fl.Row(controls=[c_l_plugs,c_l_pins,c_r_pins,c_r_plugs],alignment=fl.MainAxisAlignment.CENTER),
             fl.Row(controls=[d_configs,t_config,
                              fl.ElevatedButton('SAVE',on_click=save),
                              fl.ElevatedButton('PRINT', on_click=printer),
                              fl.IconButton(icon=fl.icons.EXIT_TO_APP_OUTLINED,icon_size=50,icon_color='red',on_click=lambda _:page.window_destroy())],
                    alignment = fl.MainAxisAlignment.CENTER))
fl.app(target=main)